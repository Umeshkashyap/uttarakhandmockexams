"""
UttarakhandMockExams — Complete Backend Server v2.0
Pure Python stdlib — zero external dependencies
All features complete: Auth, Exams, Admin, PDF, Static serving, Leaderboard, Progress
"""

import json, os, re, sys, uuid, time, threading, traceback, mimetypes, zipfile, io
import xml.etree.ElementTree as ET
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, date


sys.path.insert(0, os.path.dirname(__file__))
from database import get_conn, init_db, row_to_dict, rows_to_list
from auth_utils import hash_password, verify_password, create_token, verify_token, extract_token

PORT       = int(os.environ.get("PORT", 5000))
UPLOAD_DIR = os.path.abspath(os.environ.get("UPLOAD_DIR", "./uploads"))
STATIC_DIR = os.path.abspath(os.environ.get("STATIC_DIR", "./static"))
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "admin_registration_key_2024")
MAX_UPLOAD  = int(os.environ.get("MAX_FILE_SIZE_MB", "20")) * 1024 * 1024

for d in (UPLOAD_DIR, STATIC_DIR): os.makedirs(d, exist_ok=True)

# Copy frontend.html → static/index.html if exists
_fe = os.path.join(os.path.dirname(__file__), "frontend.html")
_si = os.path.join(STATIC_DIR, "index.html")
if os.path.exists(_fe) and not os.path.exists(_si):
    import shutil; shutil.copy(_fe, _si)

# ─────────────────────────────────────────────────────────────────────────────
def ok(data, status=200):  return status, {**data, "success": True}
def err(msg, status=400):  return status, {"success": False, "message": msg}

def get_user(headers):
    auth = headers.get("Authorization") or headers.get("authorization", "")
    if not auth: return None
    try: return verify_token(extract_token(auth))
    except: return None

def require_auth(headers):
    u = get_user(headers)
    if not u: raise PermissionError("Authentication required.")
    return u

def require_admin(headers):
    u = require_auth(headers)
    if u.get("role") != "admin": raise PermissionError("Admin access required.")
    return u

# ─────────────────────────────────────────────────────────────────────────────
# AUTH HANDLERS
# ─────────────────────────────────────────────────────────────────────────────
def auth_register(body, headers, params):
    name  = body.get("name","").strip()
    email = body.get("email","").strip().lower()
    pwd   = body.get("password","")
    if not name or not email or len(pwd) < 6:
        return err("Name, email and password (min 6 chars) are required.")
    conn = get_conn()
    try:
        if conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
            return err("Email already registered.", 409)
        uid = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO users (id,name,email,phone,password,role,exam_target) VALUES (?,?,?,?,?,'student',?)",
            (uid, name, email, body.get("phone",""), hash_password(pwd), body.get("exam_target","SSC"))
        )
        conn.commit()
        token = create_token({"id":uid,"name":name,"email":email,"role":"student"})
        return ok({"message":"Registration successful!","token":token,
                   "user":{"id":uid,"name":name,"email":email,"role":"student","exam_target":body.get("exam_target","SSC")}}, 201)
    finally: conn.close()

def auth_register_admin(body, headers, params):
    if body.get("admin_secret") != ADMIN_SECRET:
        return err("Invalid admin secret.", 403)
    name=body.get("name","").strip(); email=body.get("email","").strip().lower(); pwd=body.get("password","")
    if not name or not email or not pwd: return err("All fields required.")
    conn = get_conn()
    try:
        if conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
            return err("Email already registered.", 409)
        uid = str(uuid.uuid4())
        conn.execute("INSERT INTO users (id,name,email,password,role) VALUES (?,?,?,?,'admin')",
                     (uid, name, email, hash_password(pwd)))
        conn.commit()
        token = create_token({"id":uid,"name":name,"email":email,"role":"admin"})
        return ok({"message":"Admin created.","token":token,"user":{"id":uid,"name":name,"email":email,"role":"admin"}}, 201)
    finally: conn.close()

def auth_login(body, headers, params):
    email = body.get("email","").strip().lower()
    pwd   = body.get("password","")
    if not email or not pwd: return err("Email and password required.")
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not row or not verify_password(pwd, row["password"]):
            return err("Invalid email or password.", 401)
        u = row_to_dict(row); u.pop("password", None)
        token = create_token({"id":u["id"],"name":u["name"],"email":u["email"],"role":u["role"]})
        return ok({"message":"Login successful!","token":token,"user":u})
    finally: conn.close()

def auth_me(body, headers, params):
    uj = require_auth(headers)
    conn = get_conn()
    try:
        row = row_to_dict(conn.execute(
            "SELECT id,name,email,phone,role,exam_target,created_at FROM users WHERE id=?", (uj["id"],)
        ).fetchone())
        if not row: return err("User not found.", 404)
        stats = row_to_dict(conn.execute(
            "SELECT COUNT(*) as total, ROUND(AVG(percentage),1) as avg_score, "
            "MAX(percentage) as best_score, SUM(CASE WHEN status='submitted' THEN 1 ELSE 0 END) as completed "
            "FROM exam_attempts WHERE user_id=?", (uj["id"],)
        ).fetchone())
        return ok({"user":row,"stats":stats})
    finally: conn.close()

def auth_update_profile(body, headers, params):
    uj = require_auth(headers)
    conn = get_conn()
    try:
        conn.execute("UPDATE users SET name=?,phone=?,exam_target=?,updated_at=datetime('now') WHERE id=?",
                     (body.get("name",""), body.get("phone",""), body.get("exam_target",""), uj["id"]))
        conn.commit()
        return ok({"message":"Profile updated."})
    finally: conn.close()

def auth_change_password(body, headers, params):
    uj = require_auth(headers)
    conn = get_conn()
    try:
        row = conn.execute("SELECT password FROM users WHERE id=?", (uj["id"],)).fetchone()
        if not row or not verify_password(body.get("old_password",""), row["password"]):
            return err("Current password is incorrect.", 401)
        new_pwd = body.get("new_password","")
        if len(new_pwd) < 6: return err("New password must be at least 6 characters.")
        conn.execute("UPDATE users SET password=? WHERE id=?", (hash_password(new_pwd), uj["id"]))
        conn.commit()
        return ok({"message":"Password changed successfully."})
    finally: conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# SUBJECTS HANDLERS
# ─────────────────────────────────────────────────────────────────────────────
def subjects_list(body, headers, params):
    exam_type = params.get("exam_type",[None])[0]
    conn = get_conn()
    try:
        rows = rows_to_list(conn.execute("""
            SELECT s.*, COUNT(DISTINCT ds.id) as total_sets,
              COUNT(DISTINCT CASE WHEN ds.is_published=1 THEN ds.id END) as published_sets,
              COUNT(DISTINCT CASE WHEN ds.is_published=1 THEN q.id END) as total_q
            FROM subjects s
            LEFT JOIN daily_sets ds ON ds.subject_id=s.id
            LEFT JOIN questions q ON q.set_id=ds.id
            WHERE s.is_active=1 GROUP BY s.id ORDER BY s.sort_order
        """).fetchall())
        for s in rows:
            s["exam_types"] = json.loads(s.get("exam_types") or "[]")
        if exam_type:
            rows = [s for s in rows if exam_type.upper() in s["exam_types"]]
        return ok({"subjects":rows})
    finally: conn.close()

def subjects_create(body, headers, params):
    require_admin(headers)
    conn = get_conn()
    try:
        r = conn.execute(
            "INSERT INTO subjects (name,name_hindi,icon,color_class,exam_types,exam_category,sort_order) VALUES (?,?,?,?,?,?,?)",
            (body["name"],body.get("name_hindi",body["name"]),body.get("icon","📚"),
             body.get("color_class","c-gs"),json.dumps(body.get("exam_types",[])),
             body.get("exam_category","SSC"),body.get("sort_order",99))
        )
        conn.commit()
        return ok({"id":r.lastrowid,"message":"Subject created."}, 201)
    finally: conn.close()

def subject_sets(body, headers, params, subject_id):
    page  = int(params.get("page",[1])[0])
    limit = int(params.get("limit",[30])[0])
    exam_type = params.get("exam_type",[None])[0]
    search    = params.get("q",[None])[0]
    offset    = (page-1)*limit
    conn = get_conn()
    try:
        subj = row_to_dict(conn.execute("SELECT * FROM subjects WHERE id=? AND is_active=1",(subject_id,)).fetchone())
        if not subj: return err("Subject not found.",404)
        subj["exam_types"] = json.loads(subj.get("exam_types") or "[]")

        q = "SELECT ds.*, COUNT(qu.id) as question_count FROM daily_sets ds LEFT JOIN questions qu ON qu.set_id=ds.id WHERE ds.subject_id=? AND ds.is_published=1"
        args = [subject_id]
        if exam_type:
            q += " AND ds.exam_types LIKE ?"; args.append(f"%{exam_type.upper()}%")
        if search:
            q += " AND (ds.title LIKE ? OR ds.title_hindi LIKE ?)"; args.extend([f"%{search}%",f"%{search}%"])
        q += " GROUP BY ds.id ORDER BY ds.day_number LIMIT ? OFFSET ?"; args.extend([limit, offset])

        sets = rows_to_list(conn.execute(q, args).fetchall())
        uj = get_user(headers)
        for s in sets:
            s["exam_types"] = json.loads(s.get("exam_types") or "[]")
            s["user_status"] = "available"
            if uj:
                att = row_to_dict(conn.execute(
                    "SELECT score,percentage,status,submitted_at,correct,wrong,skipped FROM exam_attempts "
                    "WHERE user_id=? AND set_id=? AND status='submitted' ORDER BY submitted_at DESC LIMIT 1",
                    (uj["id"],s["id"])
                ).fetchone())
                prog = row_to_dict(conn.execute(
                    "SELECT best_score,attempts_count FROM user_progress WHERE user_id=? AND subject_id=? AND day_number=?",
                    (uj["id"],subject_id,s["day_number"])
                ).fetchone())
                s["user_status"] = "completed" if att else "available"
                s["last_attempt"] = att
                s["best_score"]     = prog["best_score"] if prog else None
                s["attempts_count"] = prog["attempts_count"] if prog else 0

        total = conn.execute(
            "SELECT COUNT(*) as c FROM daily_sets WHERE subject_id=? AND is_published=1",(subject_id,)
        ).fetchone()["c"]
        return ok({"subject":subj,"sets":sets,
                   "pagination":{"page":page,"limit":limit,"total":total,"pages":(total+limit-1)//limit}})
    finally: conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# EXAM HANDLERS
# ─────────────────────────────────────────────────────────────────────────────
def exam_start(body, headers, params, set_id):
    uj = require_auth(headers)
    uid = uj["id"]
    conn = get_conn()
    try:
        s = row_to_dict(conn.execute(
            "SELECT ds.*,su.name as subject_name,su.name_hindi FROM daily_sets ds "
            "JOIN subjects su ON su.id=ds.subject_id WHERE ds.id=? AND ds.is_published=1",(set_id,)
        ).fetchone())
        if not s: return err("Exam set not found.",404)

        existing = row_to_dict(conn.execute(
            "SELECT id,started_at FROM exam_attempts WHERE user_id=? AND set_id=? AND status='in_progress'",(uid,set_id)
        ).fetchone())

        if existing:
            # Check if time expired
            try:
                elapsed = int(time.time() - datetime.fromisoformat(existing["started_at"]).timestamp())
            except: elapsed = 0
            if elapsed > s["duration_min"]*60:
                _compute_and_submit(conn, {"id":existing["id"],"user_id":uid,"set_id":set_id,
                                           "started_at":existing["started_at"],"status":"in_progress"}, [])
                conn.commit()
                return err("Time expired. Exam was auto-submitted. Check your results.", 410)
            attempt_id = existing["id"]
            time_remaining = max(0, s["duration_min"]*60 - elapsed)
        else:
            attempt_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO exam_attempts (id,user_id,set_id,total_questions,max_score) VALUES (?,?,?,?,?)",
                (attempt_id,uid,set_id,s["total_questions"],s["total_questions"]*s["marking_correct"])
            )
            conn.commit()
            time_remaining = s["duration_min"]*60

        questions = rows_to_list(conn.execute(
            "SELECT id,q_number,question_en,question_hi,"
            "option_a_en,option_b_en,option_c_en,option_d_en,"
            "option_a_hi,option_b_hi,option_c_hi,option_d_hi,difficulty,tags "
            "FROM questions WHERE set_id=? ORDER BY q_number",(set_id,)
        ).fetchall())

        if not questions: return err("No questions in this set.",422)

        saved = {r["question_id"]:r for r in rows_to_list(conn.execute(
            "SELECT question_id,selected_ans,is_marked FROM attempt_answers WHERE attempt_id=?",(attempt_id,)
        ).fetchall())}

        for q in questions:
            q["tags"] = json.loads(q.get("tags") or "[]")
            sv = saved.get(q["id"])
            q["saved_answer"] = sv["selected_ans"] if sv else None
            q["is_marked"]    = sv["is_marked"] if sv else 0

        return ok({
            "attempt_id":attempt_id,"resumed":bool(existing),
            "set":{"id":s["id"],"title":s["title"],"title_hindi":s["title_hindi"],
                   "subject_name":s["subject_name"],"total_questions":s["total_questions"],
                   "duration_min":s["duration_min"],"marking_correct":s["marking_correct"],
                   "marking_wrong":s["marking_wrong"]},
            "questions":questions,"time_remaining_sec":time_remaining
        })
    finally: conn.close()

def exam_save_answer(body, headers, params, attempt_id):
    uj = require_auth(headers)
    conn = get_conn()
    try:
        if not conn.execute(
            "SELECT id FROM exam_attempts WHERE id=? AND user_id=? AND status='in_progress'",(attempt_id,uj["id"])
        ).fetchone():
            return err("Attempt not found or already submitted.",404)
        q_id=body.get("question_id"); q_num=body.get("q_number")
        sel=body.get("selected_ans"); is_marked=1 if body.get("is_marked") else 0
        if conn.execute("SELECT id FROM attempt_answers WHERE attempt_id=? AND question_id=?",(attempt_id,q_id)).fetchone():
            conn.execute("UPDATE attempt_answers SET selected_ans=?,is_marked=?,time_spent_sec=? WHERE attempt_id=? AND question_id=?",
                         (sel,is_marked,body.get("time_spent_sec",0),attempt_id,q_id))
        else:
            conn.execute("INSERT INTO attempt_answers (attempt_id,question_id,q_number,selected_ans,is_marked,time_spent_sec) VALUES (?,?,?,?,?,?)",
                         (attempt_id,q_id,q_num,sel,is_marked,body.get("time_spent_sec",0)))
        conn.commit()
        return ok({"message":"Saved."})
    finally: conn.close()

def exam_submit(body, headers, params, attempt_id):
    uj = require_auth(headers)
    conn = get_conn()
    try:
        att = row_to_dict(conn.execute("SELECT * FROM exam_attempts WHERE id=? AND user_id=?",(attempt_id,uj["id"])).fetchone())
        if not att: return err("Attempt not found.",404)
        if att["status"]=="submitted": return err("Already submitted.",409)
        result = _compute_and_submit(conn, att, body.get("answers",[]))
        conn.commit()
        return ok({"result":result})
    finally: conn.close()

def exam_result(body, headers, params, attempt_id):
    uj = require_auth(headers)
    conn = get_conn()
    try:
        att = row_to_dict(conn.execute(
            "SELECT ea.*,ds.title,ds.title_hindi,ds.marking_correct,ds.marking_wrong,ds.day_number,"
            "s.name as subject_name,s.icon FROM exam_attempts ea "
            "JOIN daily_sets ds ON ds.id=ea.set_id JOIN subjects s ON s.id=ds.subject_id "
            "WHERE ea.id=? AND ea.user_id=? AND ea.status='submitted'",(attempt_id,uj["id"])
        ).fetchone())
        if not att: return err("Result not found.",404)
        answers = rows_to_list(conn.execute(
            "SELECT aa.*,q.question_en,q.question_hi,"
            "q.option_a_en,q.option_b_en,q.option_c_en,q.option_d_en,"
            "q.option_a_hi,q.option_b_hi,q.option_c_hi,q.option_d_hi,"
            "q.correct_ans,q.explanation,q.explanation_hi,q.difficulty "
            "FROM attempt_answers aa JOIN questions q ON q.id=aa.question_id "
            "WHERE aa.attempt_id=? ORDER BY aa.q_number",(attempt_id,)
        ).fetchall())
        pct=att["percentage"]
        grade,grade_hi = (("Excellent! 🏆","उत्कृष्ट!") if pct>=85 else
                          ("Very Good 👍","बहुत अच्छा!") if pct>=70 else
                          ("Good 📚","अच्छा!") if pct>=55 else
                          ("Average","औसत") if pct>=40 else
                          ("Keep Practicing 💪","और अभ्यास करें!"))
        return ok({"attempt":att,"answers":answers,"grade":grade,"grade_hi":grade_hi,
                   "summary":{k:att[k] for k in ["correct","wrong","skipped","score","max_score","percentage","time_taken_sec"]}})
    finally: conn.close()

def exam_history(body, headers, params):
    uj = require_auth(headers)
    page=int(params.get("page",[1])[0]); limit=int(params.get("limit",[20])[0])
    subject_id=params.get("subject_id",[None])[0]
    conn = get_conn()
    try:
        q="SELECT ea.id,ea.score,ea.max_score,ea.percentage,ea.correct,ea.wrong,ea.skipped,ea.status,ea.submitted_at,ea.time_taken_sec,ds.title,ds.day_number,s.name as subject_name,s.icon FROM exam_attempts ea JOIN daily_sets ds ON ds.id=ea.set_id JOIN subjects s ON s.id=ds.subject_id WHERE ea.user_id=? AND ea.status='submitted'"
        args=[uj["id"]]
        if subject_id: q+=" AND ds.subject_id=?"; args.append(subject_id)
        q+=" ORDER BY ea.submitted_at DESC LIMIT ? OFFSET ?"; args.extend([limit,(page-1)*limit])
        attempts=rows_to_list(conn.execute(q,args).fetchall())
        total=conn.execute("SELECT COUNT(*) as c FROM exam_attempts WHERE user_id=? AND status='submitted'",(uj["id"],)).fetchone()["c"]
        return ok({"attempts":attempts,"pagination":{"page":page,"total":total}})
    finally: conn.close()

def exam_leaderboard(body, headers, params, set_id):
    conn = get_conn()
    try:
        board = rows_to_list(conn.execute(
            "SELECT u.name,ea.score,ea.percentage,ea.correct,ea.wrong,ea.time_taken_sec,ea.submitted_at "
            "FROM exam_attempts ea JOIN users u ON u.id=ea.user_id "
            "WHERE ea.set_id=? AND ea.status='submitted' ORDER BY ea.score DESC,ea.time_taken_sec ASC LIMIT 50",(set_id,)
        ).fetchall())
        set_info = row_to_dict(conn.execute(
            "SELECT ds.title,s.name as subject FROM daily_sets ds JOIN subjects s ON s.id=ds.subject_id WHERE ds.id=?",(set_id,)
        ).fetchone())
        return ok({"leaderboard":board,"set":set_info})
    finally: conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# PROGRESS HANDLERS
# ─────────────────────────────────────────────────────────────────────────────
def progress_dashboard(body, headers, params):
    uj = require_auth(headers)
    uid = uj["id"]
    conn = get_conn()
    try:
        overall = row_to_dict(conn.execute(
            "SELECT COUNT(*) as total_attempts,SUM(CASE WHEN status='submitted' THEN 1 ELSE 0 END) as completed,"
            "ROUND(AVG(CASE WHEN status='submitted' THEN percentage END),1) as avg_score,"
            "MAX(CASE WHEN status='submitted' THEN percentage END) as best_score,"
            "SUM(CASE WHEN status='submitted' THEN correct END) as total_correct,"
            "SUM(CASE WHEN status='submitted' THEN wrong END) as total_wrong "
            "FROM exam_attempts WHERE user_id=?",(uid,)
        ).fetchone())
        subject_wise = rows_to_list(conn.execute(
            "SELECT s.name,s.icon,s.name_hindi,COUNT(ea.id) as attempts,"
            "ROUND(AVG(ea.percentage),1) as avg_pct,MAX(ea.percentage) as best_pct "
            "FROM subjects s LEFT JOIN daily_sets ds ON ds.subject_id=s.id "
            "LEFT JOIN exam_attempts ea ON ea.set_id=ds.id AND ea.user_id=? AND ea.status='submitted' "
            "WHERE s.is_active=1 GROUP BY s.id ORDER BY attempts DESC",(uid,)
        ).fetchall())
        recent = rows_to_list(conn.execute(
            "SELECT ea.id,ea.score,ea.percentage,ea.correct,ea.wrong,ea.submitted_at,ea.time_taken_sec,"
            "ds.title,ds.day_number,s.name as subject,s.icon "
            "FROM exam_attempts ea JOIN daily_sets ds ON ds.id=ea.set_id "
            "JOIN subjects s ON s.id=ds.subject_id "
            "WHERE ea.user_id=? AND ea.status='submitted' ORDER BY ea.submitted_at DESC LIMIT 10",(uid,)
        ).fetchall())
        # Streak calculation
        streak_rows = rows_to_list(conn.execute(
            "SELECT DATE(submitted_at) as date FROM exam_attempts WHERE user_id=? AND status='submitted' "
            "GROUP BY DATE(submitted_at) ORDER BY date DESC LIMIT 30",(uid,)
        ).fetchall())
        streak=0
        for i,r in enumerate(streak_rows):
            exp=(datetime.utcnow().date() - __import__('datetime').timedelta(days=i)).isoformat()
            if r["date"]==exp: streak+=1
            else: break
        # Score history (last 15 attempts)
        history = rows_to_list(conn.execute(
            "SELECT ea.percentage,ea.submitted_at,s.name as subject "
            "FROM exam_attempts ea JOIN daily_sets ds ON ds.id=ea.set_id "
            "JOIN subjects s ON s.id=ds.subject_id "
            "WHERE ea.user_id=? AND ea.status='submitted' ORDER BY ea.submitted_at DESC LIMIT 15",(uid,)
        ).fetchall())
        return ok({"overall":overall,"subject_wise":subject_wise,"recent_attempts":recent,
                   "streak":streak,"history":list(reversed(history))})
    finally: conn.close()

def progress_subject(body, headers, params, subject_id):
    uj = require_auth(headers)
    conn = get_conn()
    try:
        prog = rows_to_list(conn.execute(
            "SELECT up.day_number,up.best_score,up.attempts_count,up.last_attempted,ds.title,ds.scheduled_date "
            "FROM user_progress up JOIN daily_sets ds ON ds.subject_id=up.subject_id AND ds.day_number=up.day_number "
            "WHERE up.user_id=? AND up.subject_id=? ORDER BY up.day_number",(uj["id"],subject_id)
        ).fetchall())
        stats = row_to_dict(conn.execute(
            "SELECT ROUND(AVG(best_score),1) as avg_best,MAX(best_score) as all_time_best,COUNT(*) as days_done "
            "FROM user_progress WHERE user_id=? AND subject_id=?",(uj["id"],subject_id)
        ).fetchone())
        return ok({"progress":prog,"stats":stats})
    finally: conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# ADMIN HANDLERS
# ─────────────────────────────────────────────────────────────────────────────
def admin_dashboard(body, headers, params):
    require_admin(headers)
    conn = get_conn()
    try:
        stats={
            "total_students": conn.execute("SELECT COUNT(*) as c FROM users WHERE role='student'").fetchone()["c"],
            "total_subjects": conn.execute("SELECT COUNT(*) as c FROM subjects WHERE is_active=1").fetchone()["c"],
            "total_sets":     conn.execute("SELECT COUNT(*) as c FROM daily_sets WHERE is_published=1").fetchone()["c"],
            "total_questions":conn.execute("SELECT COUNT(*) as c FROM questions").fetchone()["c"],
            "total_attempts": conn.execute("SELECT COUNT(*) as c FROM exam_attempts WHERE status='submitted'").fetchone()["c"],
            "pdf_uploads":    conn.execute("SELECT COUNT(*) as c FROM pdf_uploads").fetchone()["c"],
            "avg_score":      row_to_dict(conn.execute("SELECT ROUND(AVG(percentage),1) as a FROM exam_attempts WHERE status='submitted'").fetchone())["a"],
        }
        recent=rows_to_list(conn.execute(
            "SELECT ea.percentage,ea.submitted_at,u.name,ds.title,s.name as subject "
            "FROM exam_attempts ea JOIN users u ON u.id=ea.user_id "
            "JOIN daily_sets ds ON ds.id=ea.set_id JOIN subjects s ON s.id=ds.subject_id "
            "WHERE ea.status='submitted' ORDER BY ea.submitted_at DESC LIMIT 10"
        ).fetchall())
        subject_stats=rows_to_list(conn.execute(
            "SELECT s.name,s.icon,COUNT(ea.id) as attempts,ROUND(AVG(ea.percentage),1) as avg_pct,"
            "COUNT(DISTINCT ds.id) as total_sets,SUM(CASE WHEN ds.is_published=1 THEN 1 ELSE 0 END) as pub_sets "
            "FROM subjects s LEFT JOIN daily_sets ds ON ds.subject_id=s.id "
            "LEFT JOIN exam_attempts ea ON ea.set_id=ds.id AND ea.status='submitted' "
            "WHERE s.is_active=1 GROUP BY s.id ORDER BY attempts DESC"
        ).fetchall())
        return ok({"stats":stats,"recent_attempts":recent,"subject_stats":subject_stats})
    finally: conn.close()

def admin_list_uploads(body, headers, params):
    require_admin(headers)
    conn = get_conn()
    try:
        uploads=rows_to_list(conn.execute(
            "SELECT pu.*,s.name as subject_name,u.name as uploaded_by_name "
            "FROM pdf_uploads pu LEFT JOIN subjects s ON s.id=pu.subject_id "
            "LEFT JOIN users u ON u.id=pu.uploaded_by ORDER BY pu.uploaded_at DESC LIMIT 100"
        ).fetchall())
        return ok({"uploads":uploads})
    finally: conn.close()

def admin_upload_pdf(body, headers, params, file_data=None):
    uj = require_admin(headers)
    if not file_data: return err("No PDF file provided.",400)
    fn = re.sub(r'[^\w._-]','_',file_data.get("filename","upload.pdf"))
    saved = f"{int(time.time())}_{fn}"
    fpath = os.path.join(UPLOAD_DIR, saved)
    with open(fpath,"wb") as f: f.write(file_data["content"])
    subject_id = body.get("subject_id")
    exam_types = body.get("exam_types","[]")
    try: et=json.loads(exam_types) if isinstance(exam_types,str) else exam_types
    except: et=[]
    day_num=body.get("day_number"); sched=body.get("scheduled_date")
    conn = get_conn()
    try:
        subj=row_to_dict(conn.execute("SELECT * FROM subjects WHERE id=?",(subject_id,)).fetchone())
        if not subj: os.remove(fpath); return err("Subject not found.",404)
        r=conn.execute(
            "INSERT INTO pdf_uploads (filename,original_name,subject_id,exam_types,day_number,"
            "scheduled_date,file_size_kb,upload_status,uploaded_by) VALUES (?,?,?,?,?,?,?,'pending',?)",
            (saved,file_data["filename"],subject_id,json.dumps(et),day_num,sched,
             len(file_data["content"])//1024,uj["id"])
        ); conn.commit()
        uid = r.lastrowid
    finally: conn.close()
    threading.Thread(target=_process_pdf_async,
        args=(uid,fpath,subject_id,subj["name"],et,day_num,sched),daemon=True).start()
    return ok({"message":"PDF uploaded! Processing started...","upload_id":uid,"filename":saved},202)

def admin_upload_status(body, headers, params, upload_id):
    require_admin(headers)
    conn = get_conn()
    try:
        u=row_to_dict(conn.execute("SELECT * FROM pdf_uploads WHERE id=?",(upload_id,)).fetchone())
        if not u: return err("Upload not found.",404)
        return ok({"upload":u})
    finally: conn.close()

def admin_upload_excel(body, headers, params, file_data=None):
    """Upload Excel (.xlsx or .csv) file and import questions directly."""
    uj = require_admin(headers)
    if not file_data: return err("No file provided.", 400)
    fname = file_data.get("filename","upload.xlsx").lower()
    content = file_data["content"]
    subject_id = body.get("subject_id")
    exam_types_raw = body.get("exam_types","[]")
    day_num = body.get("day_number")
    sched   = body.get("scheduled_date")
    publish = str(body.get("auto_publish","1")) == "1"

    try: et = json.loads(exam_types_raw) if isinstance(exam_types_raw,str) else exam_types_raw
    except: et = []

    # Parse rows from xlsx or csv
    try:
        if fname.endswith(".csv"):
            import csv
            text = content.decode("utf-8-sig", errors="ignore")
            reader = csv.reader(io.StringIO(text))
            all_rows = list(reader)
        else:
            all_rows = _read_xlsx(content)
    except Exception as e:
        return err(f"Could not parse file: {e}", 422)

    if len(all_rows) < 2:
        return err("File has no data rows (need header + at least 1 question).", 422)

    # Detect header row
    header = [h.strip().lower() for h in all_rows[0]]
    data_rows = all_rows[1:]

    def col(row, *names):
        for n in names:
            for i,h in enumerate(header):
                if h == n and i < len(row): return row[i].strip()
        return ""

    questions = []
    for i, row in enumerate(data_rows):
        if not any(row): continue  # skip empty rows
        qe = col(row,"question_en","question","q","प्रश्न")
        if not qe: continue
        oa = col(row,"option_a","option_a_en","a","opt_a","विकल्प a","option a")
        ob = col(row,"option_b","option_b_en","b","opt_b","option b")
        oc = col(row,"option_c","option_c_en","c","opt_c","option c")
        od = col(row,"option_d","option_d_en","d","opt_d","option d")
        if not (oa and ob and oc and od): continue

        ca_raw = col(row,"correct_ans","correct_answer","answer","ans","answer_key","सही उत्तर").upper()
        ca = {"A":0,"B":1,"C":2,"D":3}.get(ca_raw, 0)

        questions.append({
            "q_number": len(questions)+1,
            "question_en": qe,
            "question_hi": col(row,"question_hi","question_hindi","प्रश्न_हिंदी") or None,
            "option_a_en": oa, "option_b_en": ob, "option_c_en": oc, "option_d_en": od,
            "option_a_hi": col(row,"option_a_hi","a_hindi") or None,
            "option_b_hi": col(row,"option_b_hi","b_hindi") or None,
            "option_c_hi": col(row,"option_c_hi","c_hindi") or None,
            "option_d_hi": col(row,"option_d_hi","d_hindi") or None,
            "correct_ans": ca,
            "explanation": col(row,"explanation","exp","व्याख्या") or f"Correct: {ca_raw}",
            "difficulty":  col(row,"difficulty","level","कठिनाई") or "medium",
        })

    if not questions:
        return err("No valid questions found. Check column headers.", 422)

    conn = get_conn()
    try:
        subj = row_to_dict(conn.execute("SELECT * FROM subjects WHERE id=?",(subject_id,)).fetchone())
        if not subj: return err("Subject not found.", 404)

        if not day_num:
            day_num = conn.execute(
                "SELECT COALESCE(MAX(day_number),0)+1 as n FROM daily_sets WHERE subject_id=?",(subject_id,)
            ).fetchone()["n"]

        ex = row_to_dict(conn.execute(
            "SELECT id FROM daily_sets WHERE subject_id=? AND day_number=?",(subject_id,day_num)
        ).fetchone())

        if ex:
            set_id = ex["id"]
            conn.execute("DELETE FROM questions WHERE set_id=?",(set_id,))
        else:
            r = conn.execute(
                "INSERT INTO daily_sets (subject_id,day_number,title,title_hindi,exam_types,"
                "scheduled_date,total_questions,is_published) VALUES (?,?,?,?,?,?,?,?)",
                (subject_id, day_num,
                 f"{subj['name']} — Day {day_num} Mock Test",
                 f"{subj['name']} — दिन {day_num} मॉक टेस्ट",
                 json.dumps(et), sched, len(questions), 0)
            ); conn.commit(); set_id = r.lastrowid

        for q in questions[:30]:  # max 30 per set
            conn.execute(
                "INSERT INTO questions (set_id,q_number,question_en,question_hi,"
                "option_a_en,option_b_en,option_c_en,option_d_en,"
                "option_a_hi,option_b_hi,option_c_hi,option_d_hi,"
                "correct_ans,explanation,difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (set_id,q["q_number"],q["question_en"],q["question_hi"],
                 q["option_a_en"],q["option_b_en"],q["option_c_en"],q["option_d_en"],
                 q["option_a_hi"],q["option_b_hi"],q["option_c_hi"],q["option_d_hi"],
                 q["correct_ans"],q["explanation"],q["difficulty"])
            )

        count = min(len(questions), 30)
        conn.execute("UPDATE daily_sets SET total_questions=?,is_published=? WHERE id=?",
                     (count, 1 if publish else 0, set_id))

        # Log in pdf_uploads table (reuse for all uploads)
        # Use NULL for uploaded_by if user doesn't exist in DB (avoids FK error)
        saved_name = f"excel_{int(time.time())}_{file_data['filename']}"
        uploader = uj["id"] if conn.execute("SELECT id FROM users WHERE id=?",(uj["id"],)).fetchone() else None
        conn.execute(
            "INSERT INTO pdf_uploads (filename,original_name,subject_id,exam_types,day_number,"
            "scheduled_date,file_size_kb,upload_status,extracted_count,set_id,uploaded_by,processed_at) "
            "VALUES (?,?,?,?,?,?,?,'published',?,?,?,datetime('now'))",
            (saved_name,file_data["filename"],subject_id,json.dumps(et),day_num,sched,
             len(content)//1024, count, set_id, uploader)
        )
        conn.commit()

        return ok({
            "message": f"✅ {count} questions imported and {'published' if publish else 'saved as draft'}!",
            "set_id": set_id,
            "count": count,
            "questions_imported": count,
            "total_in_file": len(questions),
            "published": publish,
        }, 201)
    finally: conn.close()

def admin_sample_excel(body, headers, params):
    """Return a sample Excel file for admins to download."""
    require_admin(headers)
    fmt = params.get("format",["xlsx"])[0]
    rows = [
        ["1","What is the capital of Uttarakhand?","उत्तराखंड की राजधानी?","Dehradun (Winter)","Nainital","Haridwar","Almora","A","Dehradun is winter capital; Gairsain is summer capital.","easy"],
        ["2","Uttarakhand was formed on which date?","उत्तराखंड का गठन?","9 November 2000","1 November 2000","26 January 2001","15 August 2000","A","Uttarakhand (27th state) formed from UP on 9 November 2000.","easy"],
        ["3","State bird of Uttarakhand?","राज्य पक्षी?","Peacock","Eagle","Monal (Himalayan Monal)","Sparrow","C","Himalayan Monal (Lophophorus impejanus) is state bird.","easy"],
        ["4","Which river merges at Devprayag to form Ganga?","देवप्रयाग में गंगा कैसे बनती है?","Yamuna+Ganga","Bhagirathi+Alaknanda","Mandakini+Alaknanda","Tons+Bhagirathi","B","Bhagirathi + Alaknanda = Ganga at Devprayag.","medium"],
        ["5","Nanda Devi peak height?","नंदा देवी की ऊँचाई?","7,500 m","7,816 m","8,000 m","7,200 m","B","Nanda Devi (7816 m) is highest peak in Uttarakhand, 2nd in India.","medium"],
    ]
    headers_row = ["q_number","question_en","question_hi","option_a","option_b","option_c","option_d","correct_ans","explanation","difficulty"]
    if fmt == "csv":
        import csv
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(headers_row)
        writer.writerows(rows)
        csv_bytes = out.getvalue().encode("utf-8-sig")
        return ("__CSV__", csv_bytes)
    else:
        xlsx_bytes = _make_xlsx(rows, headers_row)
        return ("__XLSX__", xlsx_bytes)

def _read_xlsx(data):
    """Parse xlsx binary, return list of rows (list of str)."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except Exception:
        raise ValueError("File is not a valid xlsx (zip) format.")
    strings = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        ns = {"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        for si in root.findall("s:si", ns):
            t = si.find(".//s:t", ns)
            strings.append((t.text or "") if t is not None else "")
    # Find worksheet
    ws_name = "xl/worksheets/sheet1.xml"
    for n in z.namelist():
        if n.startswith("xl/worksheets/sheet") and n.endswith(".xml"):
            ws_name = n; break
    ws = ET.fromstring(z.read(ws_name))
    ns = {"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rows = []
    for row in ws.findall(".//s:row", ns):
        cells = {}
        for c in row.findall("s:c", ns):
            ref = c.get("r","")
            col = "".join(ch for ch in ref if ch.isalpha())
            col_idx = sum((ord(ch)-64) * (26**i) for i,ch in enumerate(reversed(col))) - 1
            v = c.find("s:v", ns)
            if v is None: cells[col_idx]=""; continue
            t = c.get("t","")
            if t == "s": cells[col_idx] = strings[int(v.text)] if v.text else ""
            else: cells[col_idx] = v.text or ""
        if cells:
            mx = max(cells.keys())+1
            rows.append([cells.get(i,"") for i in range(mx)])
    return rows

def _make_xlsx(rows, hdr):
    """Create xlsx binary from rows + header list. Pure stdlib."""
    buf = io.BytesIO()
    ct = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/></Types>'
    rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    wb_rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/></Relationships>'
    wb = '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Questions" sheetId="1" r:id="rId1"/></sheets></workbook>'
    strs = []; si_map = {}
    def si(v):
        v=str(v) if v else ""
        if v not in si_map: si_map[v]=len(strs); strs.append(v)
        return si_map[v]
    all_r = [hdr]+list(rows); sheet_r = []
    for ri,row in enumerate(all_r):
        cells=""
        for ci,val in enumerate(row):
            col_letters=""
            n=ci+1
            while n>0: col_letters=chr(64+(n%26 or 26))+col_letters; n=(n-1)//26
            cells+=f'<c r="{col_letters}{ri+1}" t="s"><v>{si(val)}</v></c>'
        sheet_r.append(f'<row r="{ri+1}">{cells}</row>')
    ws_xml=f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{"".join(sheet_r)}</sheetData></worksheet>'
    def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;").replace("'","&apos;")
    ss=f'<?xml version="1.0" encoding="UTF-8"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(strs)}" uniqueCount="{len(strs)}">{"".join(f"<si><t xml:space=\'preserve\'>{esc(s)}</t></si>" for s in strs)}</sst>'
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml",ct); zf.writestr("_rels/.rels",rels)
        zf.writestr("xl/workbook.xml",wb); zf.writestr("xl/_rels/workbook.xml.rels",wb_rels)
        zf.writestr("xl/worksheets/sheet1.xml",ws_xml); zf.writestr("xl/sharedStrings.xml",ss)
    return buf.getvalue()

def admin_list_sets(body, headers, params):
    require_admin(headers)
    sid=params.get("subject_id",[None])[0]
    pub=params.get("published",[None])[0]
    conn = get_conn()
    try:
        q="SELECT ds.*,s.name as subject_name,s.icon,COUNT(qu.id) as question_count FROM daily_sets ds JOIN subjects s ON s.id=ds.subject_id LEFT JOIN questions qu ON qu.set_id=ds.id"
        args=[]; conds=[]
        if sid: conds.append("ds.subject_id=?"); args.append(sid)
        if pub is not None: conds.append("ds.is_published=?"); args.append(int(pub))
        if conds: q+=" WHERE "+" AND ".join(conds)
        q+=" GROUP BY ds.id ORDER BY ds.subject_id,ds.day_number"
        sets=rows_to_list(conn.execute(q,args).fetchall())
        return ok({"sets":sets})
    finally: conn.close()

def admin_create_set(body, headers, params):
    uj = require_admin(headers)
    conn = get_conn()
    try:
        sid=body.get("subject_id"); day=body.get("day_number")
        if conn.execute("SELECT id FROM daily_sets WHERE subject_id=? AND day_number=?",(sid,day)).fetchone():
            return err(f"Day {day} already exists for this subject.",409)
        r=conn.execute(
            "INSERT INTO daily_sets (subject_id,day_number,title,title_hindi,exam_types,"
            "scheduled_date,duration_min,marking_correct,marking_wrong,created_by) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (sid,day,body.get("title"),body.get("title_hindi",body.get("title","")),
             json.dumps(body.get("exam_types",[])),body.get("scheduled_date"),
             body.get("duration_min",45),body.get("marking_correct",4),body.get("marking_wrong",1),uj["id"])
        ); conn.commit()
        return ok({"set_id":r.lastrowid},201)
    finally: conn.close()

def admin_publish_set(body, headers, params, set_id):
    require_admin(headers)
    publish=body.get("publish",True)
    conn = get_conn()
    try:
        if not conn.execute("SELECT id FROM daily_sets WHERE id=?",(set_id,)).fetchone():
            return err("Set not found.",404)
        if publish:
            qc=conn.execute("SELECT COUNT(*) as c FROM questions WHERE set_id=?",(set_id,)).fetchone()["c"]
            if qc<1: return err("Cannot publish: add questions first.",422)
        conn.execute("UPDATE daily_sets SET is_published=? WHERE id=?",(1 if publish else 0,set_id))
        conn.commit()
        return ok({"message":"Set published! Students can now see it." if publish else "Set unpublished."})
    finally: conn.close()

def admin_bulk_publish(body, headers, params):
    require_admin(headers)
    subject_id=body.get("subject_id"); publish=body.get("publish",True)
    if not subject_id: return err("subject_id required.")
    conn = get_conn()
    try:
        if publish:
            # Only publish sets that have questions
            r=conn.execute(
                "UPDATE daily_sets SET is_published=1 WHERE subject_id=? AND (SELECT COUNT(*) FROM questions WHERE set_id=daily_sets.id)>0",
                (subject_id,)
            )
        else:
            r=conn.execute("UPDATE daily_sets SET is_published=0 WHERE subject_id=?",(subject_id,))
        conn.commit()
        return ok({"message":f"{r.rowcount} sets {'published' if publish else 'unpublished'}.",
                   "count":r.rowcount})
    finally: conn.close()

def admin_add_questions(body, headers, params, set_id):
    require_admin(headers)
    questions=body.get("questions",[])
    if not questions: return err("questions array required.",400)
    conn = get_conn()
    try:
        if not conn.execute("SELECT id FROM daily_sets WHERE id=?",(set_id,)).fetchone():
            return err("Set not found.",404)
        conn.execute("DELETE FROM questions WHERE set_id=?",(set_id,))
        for i,q in enumerate(questions):
            conn.execute(
                "INSERT INTO questions (set_id,q_number,question_en,question_hi,"
                "option_a_en,option_b_en,option_c_en,option_d_en,"
                "option_a_hi,option_b_hi,option_c_hi,option_d_hi,"
                "correct_ans,explanation,explanation_hi,difficulty,tags) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (set_id,q.get("q_number",i+1),q["question_en"],q.get("question_hi"),
                 q["option_a_en"],q["option_b_en"],q["option_c_en"],q["option_d_en"],
                 q.get("option_a_hi"),q.get("option_b_hi"),q.get("option_c_hi"),q.get("option_d_hi"),
                 q["correct_ans"],q.get("explanation"),q.get("explanation_hi"),
                 q.get("difficulty","medium"),json.dumps(q.get("tags",[])) if q.get("tags") else None)
            )
        conn.execute("UPDATE daily_sets SET total_questions=? WHERE id=?",(len(questions),set_id))
        conn.commit()
        return ok({"message":f"{len(questions)} questions saved.","count":len(questions)},201)
    finally: conn.close()

def admin_get_questions(body, headers, params, set_id):
    require_admin(headers)
    conn = get_conn()
    try:
        qs=rows_to_list(conn.execute("SELECT * FROM questions WHERE set_id=? ORDER BY q_number",(set_id,)).fetchall())
        return ok({"questions":qs})
    finally: conn.close()

def admin_update_question(body, headers, params, q_id):
    require_admin(headers)
    conn = get_conn()
    try:
        if not conn.execute("SELECT id FROM questions WHERE id=?",(q_id,)).fetchone():
            return err("Question not found.",404)
        conn.execute(
            "UPDATE questions SET question_en=?,question_hi=?,"
            "option_a_en=?,option_b_en=?,option_c_en=?,option_d_en=?,"
            "correct_ans=?,explanation=?,difficulty=? WHERE id=?",
            (body.get("question_en"),body.get("question_hi"),
             body.get("option_a_en"),body.get("option_b_en"),body.get("option_c_en"),body.get("option_d_en"),
             body.get("correct_ans"),body.get("explanation"),body.get("difficulty","medium"),q_id)
        )
        conn.commit()
        return ok({"message":"Question updated."})
    finally: conn.close()

def admin_students(body, headers, params):
    require_admin(headers)
    conn = get_conn()
    try:
        studs=rows_to_list(conn.execute(
            "SELECT u.id,u.name,u.email,u.phone,u.exam_target,u.created_at,"
            "COUNT(ea.id) as total_attempts,ROUND(AVG(ea.percentage),1) as avg_score,"
            "MAX(ea.submitted_at) as last_active "
            "FROM users u LEFT JOIN exam_attempts ea ON ea.user_id=u.id AND ea.status='submitted' "
            "WHERE u.role='student' GROUP BY u.id ORDER BY u.created_at DESC"
        ).fetchall())
        return ok({"students":studs})
    finally: conn.close()

def admin_schedule_check(body, headers, params):
    """Auto-publish sets scheduled for today"""
    require_admin(headers)
    today = date.today().isoformat()
    conn = get_conn()
    try:
        r=conn.execute(
            "UPDATE daily_sets SET is_published=1 WHERE scheduled_date=? AND is_published=0 "
            "AND (SELECT COUNT(*) FROM questions WHERE set_id=daily_sets.id)>0",(today,)
        )
        conn.commit()
        return ok({"message":f"{r.rowcount} sets auto-published for today ({today}).","count":r.rowcount})
    finally: conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# SUBMIT HELPER
# ─────────────────────────────────────────────────────────────────────────────
def _compute_and_submit(conn, att, client_answers):
    for a in client_answers:
        if not conn.execute("SELECT id FROM attempt_answers WHERE attempt_id=? AND question_id=?",
                            (att["id"],a.get("question_id"))).fetchone():
            conn.execute(
                "INSERT OR IGNORE INTO attempt_answers (attempt_id,question_id,q_number,selected_ans,is_marked) VALUES (?,?,?,?,?)",
                (att["id"],a.get("question_id"),a.get("q_number"),a.get("selected_ans"),1 if a.get("is_marked") else 0)
            )
    answers=rows_to_list(conn.execute(
        "SELECT aa.selected_ans,q.correct_ans FROM attempt_answers aa "
        "JOIN questions q ON q.id=aa.question_id WHERE aa.attempt_id=?",(att["id"],)
    ).fetchall())
    si=row_to_dict(conn.execute(
        "SELECT total_questions,marking_correct,marking_wrong,subject_id,day_number FROM daily_sets WHERE id=?",(att["set_id"],)
    ).fetchone())
    correct=wrong=skipped=0
    for a in answers:
        if a["selected_ans"] is None: skipped+=1
        elif a["selected_ans"]==a["correct_ans"]: correct+=1
        else: wrong+=1
    skipped+=max(0,si["total_questions"]-len(answers))
    score=correct*si["marking_correct"]-wrong*si["marking_wrong"]
    max_score=si["total_questions"]*si["marking_correct"]
    pct=round((correct/si["total_questions"])*100,2) if si["total_questions"] else 0
    try:
        start_ts=datetime.fromisoformat(att["started_at"]).timestamp()
        time_taken=int(time.time()-start_ts)
    except: time_taken=0
    conn.execute(
        "UPDATE attempt_answers SET is_correct=(SELECT CASE WHEN aa2.selected_ans=q.correct_ans THEN 1 ELSE 0 END "
        "FROM attempt_answers aa2 JOIN questions q ON q.id=aa2.question_id WHERE aa2.id=attempt_answers.id) "
        "WHERE attempt_id=? AND selected_ans IS NOT NULL",(att["id"],)
    )
    conn.execute(
        "UPDATE exam_attempts SET submitted_at=datetime('now'),time_taken_sec=?,"
        "correct=?,wrong=?,skipped=?,score=?,max_score=?,percentage=?,status='submitted' WHERE id=?",
        (time_taken,correct,wrong,skipped,score,max_score,pct,att["id"])
    )
    prog=row_to_dict(conn.execute(
        "SELECT best_score,attempts_count FROM user_progress WHERE user_id=? AND subject_id=? AND day_number=?",
        (att["user_id"],si["subject_id"],si["day_number"])
    ).fetchone())
    if prog:
        conn.execute(
            "UPDATE user_progress SET best_score=MAX(best_score,?),attempts_count=attempts_count+1,"
            "last_attempted=datetime('now') WHERE user_id=? AND subject_id=? AND day_number=?",
            (pct,att["user_id"],si["subject_id"],si["day_number"])
        )
    else:
        conn.execute(
            "INSERT INTO user_progress (user_id,subject_id,day_number,best_score,attempts_count,last_attempted) VALUES (?,?,?,?,1,datetime('now'))",
            (att["user_id"],si["subject_id"],si["day_number"],pct)
        )
    return {"correct":correct,"wrong":wrong,"skipped":skipped,"score":score,"max_score":max_score,"percentage":pct,"time_taken_sec":time_taken}

# ─────────────────────────────────────────────────────────────────────────────
# PDF PROCESSING
# ─────────────────────────────────────────────────────────────────────────────
def _process_pdf_async(upload_id,filepath,subject_id,subject_name,exam_types,day_number,scheduled_date):
    conn=get_conn()
    try:
        conn.execute("UPDATE pdf_uploads SET upload_status='processing' WHERE id=?",(upload_id,)); conn.commit()
        questions=_extract_questions(filepath)
        if not questions: raise ValueError("No MCQ questions found in PDF.")
        conn.execute("UPDATE pdf_uploads SET upload_status='extracted',extracted_count=? WHERE id=?",(len(questions),upload_id)); conn.commit()
        if not day_number:
            day_number=conn.execute("SELECT COALESCE(MAX(day_number),0)+1 as n FROM daily_sets WHERE subject_id=?",(subject_id,)).fetchone()["n"]
        ex=row_to_dict(conn.execute("SELECT id FROM daily_sets WHERE subject_id=? AND day_number=?",(subject_id,day_number)).fetchone())
        if ex:
            set_id=ex["id"]
        else:
            r=conn.execute(
                "INSERT INTO daily_sets (subject_id,day_number,title,title_hindi,exam_types,scheduled_date,pdf_source,is_published) VALUES (?,?,?,?,?,?,?,0)",
                (subject_id,day_number,f"{subject_name} — Day {day_number} Mock Test",
                 f"{subject_name} — दिन {day_number} मॉक टेस्ट",json.dumps(exam_types),
                 scheduled_date,os.path.basename(filepath))
            ); conn.commit(); set_id=r.lastrowid
        conn.execute("DELETE FROM questions WHERE set_id=?",(set_id,))
        for i,q in enumerate(questions[:30]):
            opts=q.get("options",["A","B","C","D"])
            while len(opts)<4: opts.append("N/A")
            conn.execute(
                "INSERT INTO questions (set_id,q_number,question_en,question_hi,"
                "option_a_en,option_b_en,option_c_en,option_d_en,correct_ans,explanation,difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (set_id,i+1,q.get("question_en",""),q.get("question_hi"),opts[0],opts[1],opts[2],opts[3],
                 q.get("correct_ans",0),q.get("explanation"),q.get("difficulty","medium"))
            )
        count=min(len(questions),30)
        if count>=10: conn.execute("UPDATE daily_sets SET is_published=1,total_questions=? WHERE id=?",(count,set_id))
        conn.execute("UPDATE pdf_uploads SET upload_status='published',extracted_count=?,set_id=?,processed_at=datetime('now') WHERE id=?",(count,set_id,upload_id))
        conn.commit()
        print(f"[PDF] Upload {upload_id}: {count} questions → set {set_id}")
    except Exception as e:
        print(f"[PDF] Upload {upload_id} failed: {e}")
        conn.execute("UPDATE pdf_uploads SET upload_status='failed',error_message=? WHERE id=?",(str(e),upload_id)); conn.commit()
    finally: conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# T6 — IMPROVED PDF EXTRACTION ENGINE
# 5 strategies: stream text, cross-ref text, ASCII fallback, line-join, Claude AI
# Full Hindi support, smart MCQ parser, validation, explanation extraction
# ─────────────────────────────────────────────────────────────────────────────

def _extract_questions(filepath):
    """Extract MCQ questions from a PDF file using multiple strategies."""
    with open(filepath, "rb") as f:
        data = f.read()

    text = _pdf_to_text(data)

    # Strategy: Try Claude AI if API key available and text is short/garbled
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if anthropic_key and (len(text.strip()) < 200 or _looks_garbled(text)):
        try:
            ai_questions = _extract_with_claude(data, anthropic_key)
            if ai_questions and len(ai_questions) >= 3:
                return ai_questions
        except Exception as e:
            print(f"[PDF] Claude AI extraction failed: {e}")

    questions = _parse_mcqs_v2(text)

    # If nothing found, try raw ASCII fallback
    if not questions:
        ascii_text = ''.join(chr(b) if 32 <= b < 127 or b in (9, 10, 13) else ' ' for b in data)
        questions = _parse_mcqs_v2(ascii_text)

    return questions


def _pdf_to_text(data):
    """Extract text from PDF binary using multiple methods."""
    # Method 1: Standard BT...ET stream with Tj/TJ operators
    chunks = []
    for bt_block in re.finditer(rb'BT(.*?)ET', data, re.DOTALL):
        block = bt_block.group(1)
        # Tj operator: (text)Tj
        for m in re.finditer(rb'\(([^)]*)\)\s*Tj', block):
            try:    chunks.append(m.group(1).decode('utf-8', errors='replace'))
            except: chunks.append(m.group(1).decode('latin-1', errors='replace'))
        # TJ operator: [(text) num (text)] TJ
        for m in re.finditer(rb'\[([^\]]*)\]\s*TJ', block):
            inner = m.group(1)
            for part in re.finditer(rb'\(([^)]*)\)', inner):
                try:    chunks.append(part.group(1).decode('utf-8', errors='replace'))
                except: chunks.append(part.group(1).decode('latin-1', errors='replace'))
        # Add newline at end of each BT block
        chunks.append('\n')

    text1 = ' '.join(chunks)

    # Method 2: Extract text from stream objects (compressed content)
    text2_chunks = []
    for stream in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream', data, re.DOTALL):
        raw = stream.group(1)
        # Try to decode as text directly
        try:
            decoded = raw.decode('utf-8', errors='ignore')
            # Extract readable strings
            words = re.findall(r'[A-Za-z\u0900-\u097F][A-Za-z\u0900-\u097F\s,.:;?!0-9]{3,}', decoded)
            if words:
                text2_chunks.extend(words)
        except:
            pass

    text2 = ' '.join(text2_chunks)

    # Method 3: Direct string extraction from PDF objects
    text3_chunks = []
    for m in re.finditer(rb'\(([^)]{5,300})\)', data):
        raw = m.group(1)
        # Skip binary-looking content
        printable = sum(1 for b in raw if 32 <= b < 127)
        if printable / max(len(raw), 1) > 0.7:
            try:    text3_chunks.append(raw.decode('utf-8', errors='replace'))
            except: text3_chunks.append(raw.decode('latin-1', errors='replace'))

    text3 = '\n'.join(text3_chunks)

    # Pick the best extraction
    candidates = [(text1, 'stream'), (text2, 'decoded'), (text3, 'strings')]
    best = max(candidates, key=lambda x: _score_text(x[0]))
    text = best[0]

    # Post-process: clean up PDF escape sequences
    text = re.sub(r'\\n', '\n', text)
    text = re.sub(r'\\r', '\r', text)
    text = re.sub(r'\\t', '\t', text)
    text = re.sub(r'\\\(', '(', text)
    text = re.sub(r'\\\)', ')', text)
    text = re.sub(r'\\\\', '\\\\', text)
    text = re.sub(r'[ \t]{3,}', '  ', text)
    text = re.sub(r'\n{4,}', '\n\n', text)

    return text.strip()


def _score_text(text):
    """Score text quality — higher = better extraction."""
    if not text: return 0
    # Count question markers
    q_count = len(re.findall(r'(?:Q\.?\s*\d+|^\d+[.)]\s)', text, re.MULTILINE))
    # Count option markers
    opt_count = len(re.findall(r'(?:\([AaBbCcDd]\)|\b[AaBbCcDd][.)])', text))
    # Count answer markers
    ans_count = len(re.findall(r'(?:Ans(?:wer)?|सही उत्तर|उत्तर)\s*[:\-]', text, re.IGNORECASE))
    # Count readable words
    word_count = len(re.findall(r'\b[A-Za-z\u0900-\u097F]{3,}\b', text))
    return q_count * 10 + opt_count * 5 + ans_count * 8 + min(word_count, 500)


def _looks_garbled(text):
    """Check if text appears garbled/unreadable."""
    if not text or len(text.strip()) < 10: return True
    # Check ratio of printable readable words
    words = re.findall(r'\b[A-Za-z\u0900-\u097F]{3,}\b', text)
    return len(words) < 5


def _parse_mcqs_v2(text):
    """
    T6 Improved MCQ Parser v3.
    Handles: Q.1/Q1./1./1) formats, (A)(B)(C)(D) and A.B.C.D options,
    Hindi (अ)(ब)(स)(द) options, bilingual questions, explanations, difficulty.
    """
    questions = []
    if not text: return questions
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', text)

    q_split_pattern = (
        r'(?:^|\n)\s*'
        r'(?:'
        r'(?:Q|प्र|प्रश्न)[.\s]\s*(\d{1,3})[\s.):\-]'   # Q.1 / Q 1
        r'|'
        r'(?:Q|प्र|प्रश्न)\s*(\d{1,3})\s*[.):\-]\s+'    # Q1. / Q1)
        r'|'
        r'(\d{1,3})\s*[.):\-]\s+'                         # 1. / 1) / 1:
        r')'
    )
    parts = re.split(q_split_pattern, '\n' + text, flags=re.MULTILINE)
    i = 1
    while i < len(parts) - 1:
        # Pattern has 3 capture groups; pick whichever matched
        raw = parts[i]
        try: qnum = int(raw) if raw else None
        except: qnum = None
        if qnum is None:
            i += 4; continue   # skip 3 groups + content
        # Advance past all 3 groups to content
        # re.split with N groups produces N+1 parts between groups
        # Groups: (g1, g2, g3) per match; find content after all three
        block = ''
        for j in range(i + 1, min(i + 4, len(parts))):
            if parts[j] and not parts[j].strip().isdigit():
                block = parts[j]
                i = j + 1
                break
        else:
            i += 4
        if not (1 <= qnum <= 100): continue
        q = _parse_single_question(qnum, block)
        if q:
            questions.append(q)
            if len(questions) >= 30: break
    if not questions:
        questions = _parse_mcqs_block(text)
    return questions


def _parse_single_question(qnum, block):
    """Parse one question block into structured dict."""
    block = block.strip()
    if len(block) < 10: return None
    # Stop at next question marker
    next_q = re.search(r'\n\s*(?:Q\.?\s*|Q\s+)?\d{1,3}\s*[.):\-]\s+', block, re.MULTILINE)
    if next_q: block = block[:next_q.start()]

    OPT_LATIN  = r'(?:^|\n)\s*[\(\[]?\s*([AaBbCcDd])\s*[\)\].:\-]\s*'
    OPT_HINDI  = r'(?:^|\n)\s*[\(\[]?\s*(अ|ब|स|द)\s*[\)\].]?\s*'
    OPT_INLINE = r'[\(\[]([ AaBbCcDdअबसद])[\)\]]\s*([^()\[\]]{3,80})'
    ANS_PAT    = (r'(?:Ans(?:wer)?|सही\s*उत्तर|उत्तर|Correct\s*(?:Ans(?:wer)?)?|Answer\s*Key)'
                  r'\s*[:\-–=]?\s*[\(\[]?\s*([AaBbCcDd1-4अबसद])\s*[\)\]]?')
    EXP_PAT    = (r'(?:Exp(?:lanation)?|व्याख्या|Note|Hint|Reason)\s*[:\-]?\s*'
                  r'(.{10,400}?)(?=\n\n|\Z|Q\.?\s*\d+)')

    latin_m  = list(re.finditer(OPT_LATIN,  block, re.MULTILINE))
    hindi_m  = list(re.finditer(OPT_HINDI,  block, re.MULTILINE))
    opt_dict = {}

    if len(latin_m) >= 2:
        ans_line_pat = r'(?:Ans(?:wer)?|उत्तर|सही\s*उत्तर|Correct)'
        for j, m in enumerate(latin_m[:4]):
            key = m.group(1).upper(); start = m.end()
            end = latin_m[j+1].start() if j+1 < len(latin_m) else len(block)
            ans_ahead = re.search(ans_line_pat, block[start:], re.IGNORECASE)
            if ans_ahead: end = min(end, start + ans_ahead.start())
            val = re.sub(r'\s+', ' ', block[start:end]).strip()
            opt_dict[key] = val[:250]
        first_opt_pos = latin_m[0].start()
    elif len(hindi_m) >= 2:
        H2L = {'अ':'A','ब':'B','स':'C','द':'D'}
        for j, m in enumerate(hindi_m[:4]):
            key = H2L.get(m.group(1), 'A'); start = m.end()
            end = hindi_m[j+1].start() if j+1 < len(hindi_m) else len(block)
            opt_dict[key] = re.sub(r'\s+', ' ', block[start:end]).strip()[:250]
        first_opt_pos = hindi_m[0].start()
    else:
        inline = re.findall(OPT_INLINE, block)
        if len(inline) >= 2:
            for k, v in inline[:4]:
                key = k.strip().upper()
                if key in ('A','B','C','D'): opt_dict[key] = v.strip()[:250]
            first_opt_pos = block.find(f'({inline[0][0]})')
        else:
            return None

    opts = [opt_dict.get(k,'') for k in ('A','B','C','D')]
    while len(opts) < 4: opts.append('N/A')
    opts = [re.sub(r'\s+', ' ', o).strip() for o in opts]
    if not opts[0]: return None

    # Extract question text before first option
    qt_raw = block[:first_opt_pos].strip()
    qt = re.sub(r'^(?:Q\s*\.?\s*\d+\s*\.?\s*|(?:Q\.?\s*)?\d+\s*[.):\-]\s*)', '', qt_raw).strip()
    qt = re.sub(r'\s+', ' ', qt).strip()
    if len(qt) < 5: return None

    # Separate Hindi/English
    dev = re.findall(r'[\u0900-\u097F\u0966-\u096F]', qt)
    dev_ratio = len(dev) / max(len(qt), 1)
    if dev_ratio > 0.6:
        question_hi = qt
        eng_m = re.search(r'\(([A-Za-z][^)]{5,150})\)', qt)
        question_en = eng_m.group(1).strip() if eng_m else qt
    elif dev_ratio > 0.1:
        hindi_w = ' '.join(re.findall(r'[\u0900-\u097F\u0966-\u096F][\u0900-\u097F\u0966-\u096F\s,।?!]{2,}', qt))
        eng_w = re.sub(r'[\u0900-\u097F\u0966-\u096F।]+', ' ', qt)
        eng_w = re.sub(r'\([^a-zA-Z][^)]*\)', '', eng_w)
        eng_w = re.sub(r'\s+', ' ', eng_w).strip()
        question_hi = hindi_w.strip() if len(hindi_w.strip()) > 5 else None
        question_en = eng_w if len(eng_w) > 5 else qt
    else:
        question_en = qt; question_hi = None

    question_en = question_en[:500].strip()
    question_hi = question_hi[:500].strip() if question_hi else None

    # Correct answer
    ans_match = re.search(ANS_PAT, block, re.IGNORECASE)
    if ans_match:
        raw = ans_match.group(1)
        ca = {'A':0,'B':1,'C':2,'D':3,'a':0,'b':1,'c':2,'d':3,
              '1':0,'2':1,'3':2,'4':3,'अ':0,'ब':1,'स':2,'द':3}.get(raw, 0)
    else: ca = 0

    # Explanation
    exp_m = re.search(EXP_PAT, block, re.IGNORECASE | re.DOTALL)
    explanation = (re.sub(r'\s+', ' ', exp_m.group(1)).strip()[:500]
                   if exp_m else f"Correct answer: {chr(65+ca)}")

    # Difficulty
    diff_m = re.search(r'\b(easy|medium|hard|सरल|मध्यम|कठिन)\b', block, re.IGNORECASE)
    if diff_m:
        d = diff_m.group(1).lower()
        difficulty = ('easy' if d in ('easy','सरल') else 'hard' if d in ('hard','कठिन') else 'medium')
    else: difficulty = 'medium'

    return {"q_number":qnum,"question_en":question_en,"question_hi":question_hi,
            "options":opts,"correct_ans":ca,"explanation":explanation,"difficulty":difficulty}


def _parse_mcqs_block(text):
    """Fallback: block-based extraction for non-numbered formats."""
    questions = []; q_counter = 0
    blocks = re.split(r'\n{2,}', text.strip())
    for block in blocks:
        block = block.strip()
        if not block or len(block) < 15: continue
        has_opts = bool(re.search(r'(?:\(|^)\s*[AaBbCcDd]\s*[\).:\-]|[\(\[]अ[\)\]]', block, re.MULTILINE))
        if not has_opts: continue
        q_counter += 1
        q = _parse_single_question(q_counter, block)
        if q:
            questions.append(q)
            if len(questions) >= 30: break
    return questions


def _extract_with_claude(pdf_data, api_key):
    """
    Use Claude AI to extract questions from PDF when regex fails.
    Sends base64-encoded PDF to Claude's API.
    """
    import base64
    import urllib.request
    import urllib.error

    # Limit size to avoid huge API calls
    if len(pdf_data) > 5 * 1024 * 1024:  # 5MB limit
        pdf_data = pdf_data[:5 * 1024 * 1024]

    b64 = base64.standard_b64encode(pdf_data).decode('utf-8')

    prompt = """Extract ALL MCQ questions from this PDF. Return ONLY a JSON array, no other text.

Each question object must have these exact keys:
{
  "q_number": 1,
  "question_en": "Question text in English (or transliterated Hindi)",
  "question_hi": "Question text in Hindi/Devanagari (or null)",
  "option_a": "Option A text",
  "option_b": "Option B text",
  "option_c": "Option C text",
  "option_d": "Option D text",
  "correct_ans": 0,
  "explanation": "Why this answer is correct",
  "difficulty": "easy"
}

Rules:
- correct_ans: 0=A, 1=B, 2=C, 3=D
- difficulty: "easy", "medium", or "hard"
- Extract ALL questions found (max 30)
- If question is in Hindi, put it in question_hi and translate/transliterate for question_en
- Return [] if no MCQ questions found
- Return ONLY the JSON array, starting with [ and ending with ]"""

    payload = json.dumps({
        "model": "claude-opus-4-5",
        "max_tokens": 4000,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": b64,
                    }
                },
                {"type": "text", "text": prompt}
            ]
        }]
    }).encode('utf-8')

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode('utf-8'))

    raw_text = result['content'][0]['text'].strip()

    # Extract JSON array from response
    json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
    if not json_match:
        return []

    ai_questions = json.loads(json_match.group())
    questions = []
    for i, q in enumerate(ai_questions[:30], 1):
        if not q.get('question_en') and not q.get('question_hi'):
            continue
        opts = [
            q.get('option_a', 'N/A'), q.get('option_b', 'N/A'),
            q.get('option_c', 'N/A'), q.get('option_d', 'N/A'),
        ]
        questions.append({
            "q_number": q.get('q_number', i),
            "question_en": q.get('question_en', q.get('question_hi', ''))[:500],
            "question_hi": q.get('question_hi')[:500] if q.get('question_hi') else None,
            "options": opts,
            "correct_ans": int(q.get('correct_ans', 0)),
            "explanation": q.get('explanation', f"Correct answer: {chr(65+int(q.get('correct_ans',0)))}"),
            "difficulty": q.get('difficulty', 'medium'),
        })
    return questions

# ─────────────────────────────────────────────────────────────────────────────
# HTTP SERVER
# ─────────────────────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self,fmt,*args): pass  # suppress default logs

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type,Authorization')

    def _json(self,status,data):
        body=json.dumps(data,ensure_ascii=False,default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',len(body))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _file(self,path):
        if not os.path.exists(path): return False
        mime,_=mimetypes.guess_type(path)
        with open(path,'rb') as f: data=f.read()
        self.send_response(200)
        self.send_header('Content-Type',mime or 'application/octet-stream')
        self.send_header('Content-Length',len(data))
        self._cors()
        self.end_headers()
        self.wfile.write(data)
        return True

    def _parse_multipart(self,body,ct):
        bm=re.search(r'boundary=([^\s;]+)',ct)
        if not bm: return {},None
        boundary=bm.group(1).encode()
        fields={}; file_data=None
        for part in body.split(b'--'+boundary)[1:]:
            if part in(b'--\r\n',b'--'): continue
            he=part.find(b'\r\n\r\n')
            if he==-1: continue
            hdr=part[:he].decode('utf-8',errors='ignore')
            content=part[he+4:]
            if content.endswith(b'\r\n'): content=content[:-2]
            nm=re.search(r'name="([^"]+)"',hdr); fn=re.search(r'filename="([^"]+)"',hdr)
            if not nm: continue
            if fn: file_data={"filename":fn.group(1),"content":content}
            else: fields[nm.group(1)]=content.decode('utf-8',errors='ignore')
        return fields,file_data

    def _handle(self,method):
        p=urlparse(self.path); path=p.path.rstrip('/'); params=parse_qs(p.query)
        headers=dict(self.headers)
        body={}; file_data=None
        cl=int(self.headers.get('Content-Length',0))
        ct=self.headers.get('Content-Type','')
        if cl>0 and method in('POST','PUT','PATCH'):
            raw=self.rfile.read(cl)
            if 'multipart/form-data' in ct: body,file_data=self._parse_multipart(raw,ct)
            else:
                try: body=json.loads(raw.decode('utf-8'))
                except: body={}
        if method=='OPTIONS':
            self.send_response(200); self._cors(); self.end_headers(); return

        # Static file serving
        if method=='GET' and not path.startswith('/api'):
            if path in('','/','/app'): sp=os.path.join(STATIC_DIR,'index.html')
            else: sp=os.path.join(STATIC_DIR,path.lstrip('/'))
            if self._file(sp): return
            # Try index.html for SPA routing
            idx=os.path.join(STATIC_DIR,'index.html')
            if self._file(idx): return

        status,resp=self._route(method,path,body,headers,params,file_data)
        # Handle special binary file responses (xlsx/csv downloads)
        if isinstance(resp, tuple) and len(resp)==2 and resp[0] in ('__XLSX__','__CSV__'):
            file_type, file_bytes = resp
            if file_type == '__XLSX__':
                ct_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                fname = 'sample_questions.xlsx'
            else:
                ct_type = 'text/csv; charset=utf-8'
                fname = 'sample_questions.csv'
            self.send_response(200)
            self.send_header('Content-Type', ct_type)
            self.send_header('Content-Disposition', f'attachment; filename="{fname}"')
            self.send_header('Content-Length', len(file_bytes))
            self._cors()
            self.end_headers()
            self.wfile.write(file_bytes)
            return
        self._json(status,resp)

    def _route(self,method,path,body,headers,params,file_data):
        try:
            # Health / Info
            if path in('','/health','/api'):
                return ok({"service":"UttarakhandMockExams API v2","status":"ok",
                           "timestamp":datetime.utcnow().isoformat(),
                           "endpoints":["/api/auth","/api/subjects","/api/exams","/api/admin","/api/progress"]})

            # ── Auth ─────────────────────────────────────────────────────────
            if path=='/api/auth/register' and method=='POST': return auth_register(body,headers,params)
            if path=='/api/auth/register-admin' and method=='POST': return auth_register_admin(body,headers,params)
            if path=='/api/auth/login' and method=='POST': return auth_login(body,headers,params)
            if path=='/api/auth/me' and method=='GET': return auth_me(body,headers,params)
            if path=='/api/auth/profile' and method=='PUT': return auth_update_profile(body,headers,params)
            if path=='/api/auth/change-password' and method=='POST': return auth_change_password(body,headers,params)

            # ── Subjects ─────────────────────────────────────────────────────
            if path=='/api/subjects' and method=='GET': return subjects_list(body,headers,params)
            if path=='/api/subjects' and method=='POST': return subjects_create(body,headers,params)
            m=re.match(r'^/api/subjects/(\d+)/sets$',path)
            if m and method=='GET': return subject_sets(body,headers,params,m.group(1))

            # ── Exams ─────────────────────────────────────────────────────────
            if path=='/api/exams/history' and method=='GET': return exam_history(body,headers,params)
            m=re.match(r'^/api/exams/(\d+)/start$',path)
            if m and method=='POST': return exam_start(body,headers,params,m.group(1))
            m=re.match(r'^/api/exams/attempts/([^/]+)/answer$',path)
            if m and method=='PUT': return exam_save_answer(body,headers,params,m.group(1))
            m=re.match(r'^/api/exams/attempts/([^/]+)/submit$',path)
            if m and method=='POST': return exam_submit(body,headers,params,m.group(1))
            m=re.match(r'^/api/exams/attempts/([^/]+)/result$',path)
            if m and method=='GET': return exam_result(body,headers,params,m.group(1))
            m=re.match(r'^/api/exams/leaderboard/(\d+)$',path)
            if m: return exam_leaderboard(body,headers,params,m.group(1))

            # ── Progress ─────────────────────────────────────────────────────
            if path=='/api/progress/dashboard' and method=='GET': return progress_dashboard(body,headers,params)
            m=re.match(r'^/api/progress/subject/(\d+)$',path)
            if m and method=='GET': return progress_subject(body,headers,params,m.group(1))

            # ── Admin ─────────────────────────────────────────────────────────
            if path=='/api/admin/dashboard' and method=='GET': return admin_dashboard(body,headers,params)
            if path=='/api/admin/uploads' and method=='GET': return admin_list_uploads(body,headers,params)
            if path=='/api/admin/upload-pdf' and method=='POST': return admin_upload_pdf(body,headers,params,file_data)
            if path=='/api/admin/upload-excel' and method=='POST': return admin_upload_excel(body,headers,params,file_data)
            if path in ('/api/admin/sample-excel','/api/admin/sample-file') and method=='GET':
                result = admin_sample_excel(body,headers,params)
                fmt = params.get("format",["xlsx"])[0]
                return result  # handled specially below
            if path=='/api/admin/sets' and method=='GET': return admin_list_sets(body,headers,params)
            if path=='/api/admin/sets' and method=='POST': return admin_create_set(body,headers,params)
            if path=='/api/admin/students' and method=='GET': return admin_students(body,headers,params)
            if path=='/api/admin/bulk-publish' and method=='POST': return admin_bulk_publish(body,headers,params)
            if path=='/api/admin/schedule-check' and method=='POST': return admin_schedule_check(body,headers,params)
            m=re.match(r'^/api/admin/uploads/(\d+)/status$',path)
            if m and method=='GET': return admin_upload_status(body,headers,params,m.group(1))
            m=re.match(r'^/api/admin/sets/(\d+)/publish$',path)
            if m and method=='PUT': return admin_publish_set(body,headers,params,m.group(1))
            m=re.match(r'^/api/admin/sets/(\d+)/questions$',path)
            if m and method=='POST': return admin_add_questions(body,headers,params,m.group(1))
            if m and method=='GET': return admin_get_questions(body,headers,params,m.group(1))
            m=re.match(r'^/api/admin/questions/(\d+)$',path)
            if m and method=='PUT': return admin_update_question(body,headers,params,m.group(1))

            return err(f"Route not found: {method} {path}",404)
        except PermissionError as e: return err(str(e),403)
        except Exception as e:
            traceback.print_exc()
            return err(str(e),500)

    def do_GET(self):    self._handle('GET')
    def do_POST(self):   self._handle('POST')
    def do_PUT(self):    self._handle('PUT')
    def do_DELETE(self): self._handle('DELETE')
    def do_OPTIONS(self):self._handle('OPTIONS')
    def do_PATCH(self):  self._handle('PATCH')

# ─────────────────────────────────────────────────────────────────────────────
# SCHEDULER — auto-publish sets for today every hour
# ─────────────────────────────────────────────────────────────────────────────
def _scheduler():
    while True:
        time.sleep(3600)
        try:
            today=date.today().isoformat()
            conn=get_conn()
            r=conn.execute(
                "UPDATE daily_sets SET is_published=1 WHERE scheduled_date=? AND is_published=0 "
                "AND (SELECT COUNT(*) FROM questions WHERE set_id=daily_sets.id)>0",(today,)
            )
            conn.commit(); conn.close()
            if r.rowcount: print(f"[Scheduler] Auto-published {r.rowcount} sets for {today}")
        except Exception as e: print(f"[Scheduler] Error: {e}")

def run():
    init_db()
    # Copy frontend to static dir
    fe=os.path.join(os.path.dirname(__file__),"frontend.html")
    si=os.path.join(STATIC_DIR,"index.html")
    if os.path.exists(fe):
        import shutil; shutil.copy(fe,si)
        print(f"[Static] Frontend copied → {si}")
    threading.Thread(target=_scheduler,daemon=True).start()
    server=HTTPServer(('0.0.0.0',PORT),Handler)
    print(f"\n{'='*50}")
    print(f"  🚀  UttarakhandMockExams API v2.0")
    print(f"  📡  API:      http://localhost:{PORT}/api")
    print(f"  🌐  Frontend: http://localhost:{PORT}/")
    print(f"  ❤️   Health:   http://localhost:{PORT}/health")
    print(f"  📁  Uploads:  {UPLOAD_DIR}")
    print(f"{'='*50}\n")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\n[Server] Shutting down."); server.shutdown()

if __name__=='__main__': run()
