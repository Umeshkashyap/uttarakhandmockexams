"""
UttarakhandMockExams — Master Seed Script (T8 Final)
Seeds: UK (8) + UP (9) + SSC (9) = 26 subjects, 780 sets, 23,400 questions
Run: python3 seed.py
"""
import sys, os, json, uuid
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DB_PATH", "./uttarakhandmockexams.db")
from database import init_db, get_conn
from auth_utils import hash_password
from datetime import date, timedelta

def load_questions():
    all_subjects = []
    for mod, label in [("uk_questions","UK"),("up_questions","UP"),("ssc_questions","SSC")]:
        try:
            m = __import__(mod)
            subs = getattr(m, f"{label.replace('SSC','SSC')}_SUBJECTS" if label!="SSC" else "SSC_SUBJECTS")
            qs   = getattr(m, f"{label.replace('SSC','SSC')}_QUESTIONS" if label!="SSC" else "SSC_QUESTIONS")
            for s in subs:
                all_subjects.append((s, qs.get(s["name"], [])))
            print(f"  📦  {label}: {len(subs)} subjects loaded")
        except ImportError:
            print(f"  ⚠️   {mod}.py not found")
    return all_subjects

def seed():
    print("\n🌱  Seeding UttarakhandMockExams...\n")
    init_db()
    conn = get_conn()
    print("  🗑️   Clearing old data...")
    conn.executescript("""
        DELETE FROM attempt_answers; DELETE FROM exam_attempts;
        DELETE FROM user_progress;   DELETE FROM pdf_uploads;
        DELETE FROM questions;       DELETE FROM daily_sets;
        DELETE FROM subjects;        DELETE FROM users;
    """)
    conn.commit()
    print("\n  📚  Loading question banks...")
    all_subjects = load_questions()
    if not all_subjects:
        print("  ❌  No question banks found!"); conn.close(); return
    print(f"\n  🌱  Seeding {len(all_subjects)} subjects...\n")
    total_sets = total_q = 0
    for subj, bank in all_subjects:
        cur = conn.execute(
            "INSERT INTO subjects (name,name_hindi,icon,color_class,exam_types,sort_order,is_active) VALUES (?,?,?,?,?,?,1)",
            (subj["name"],subj["name_hindi"],subj["icon"],subj["color_class"],
             json.dumps(subj["exam_types"]),subj["sort_order"]))
        sid = cur.lastrowid
        et_json = json.dumps(subj["exam_types"])
        for day in range(1, 31):
            sched = (date(2026,4,1)+timedelta(days=day-1)).isoformat()
            r = conn.execute(
                "INSERT INTO daily_sets (subject_id,day_number,title,title_hindi,exam_types,scheduled_date,total_questions,is_published) VALUES (?,?,?,?,?,?,30,?)",
                (sid,day,f"{subj['name']} — Day {day} Mock Test",f"{subj['name']} — दिन {day} मॉक टेस्ट",
                 et_json,sched,1 if day<=5 else 0))
            set_id = r.lastrowid; total_sets += 1
            for qn in range(1,31):
                tpl = bank[(qn-1)%len(bank)] if bank else {}
                if tpl:
                    conn.execute(
                        "INSERT INTO questions (set_id,q_number,question_en,question_hi,option_a_en,option_b_en,option_c_en,option_d_en,correct_ans,explanation,difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (set_id,qn,tpl["qe"],tpl.get("qh"),tpl["opts"][0],tpl["opts"][1],tpl["opts"][2],tpl["opts"][3],
                         tpl["ans"],tpl.get("exp",""),tpl.get("diff","medium")))
                else:
                    conn.execute(
                        "INSERT INTO questions (set_id,q_number,question_en,correct_ans,option_a_en,option_b_en,option_c_en,option_d_en) VALUES (?,?,?,?,?,?,?,?)",
                        (set_id,qn,f"{subj['name']} Q{qn} — Upload PDF to replace",qn%4,"Option A","Option B","Option C","Option D"))
                total_q += 1
        conn.commit()
        print(f"  ✓  {subj['icon']}  {subj['name']}  (id={sid}, {len(bank)} unique Qs)")
    # Users
    conn.execute("INSERT INTO users (id,name,email,password,role) VALUES (?,?,?,?,'admin')",
        (str(uuid.uuid4()),"Admin","admin@uttarakhandmockexams.in",hash_password("admin123")))
    conn.execute("INSERT INTO users (id,name,email,phone,password,role,exam_target) VALUES (?,?,?,?,?,'student','UKPSC')",
        (str(uuid.uuid4()),"Rahul Sharma","rahul@example.com","9876543210",hash_password("demo123")))
    conn.commit(); conn.close()
    n = len(all_subjects)
    uk = sum(1 for s,_ in all_subjects if "UKPSC" in s["exam_types"] or "UKSSC" in s["exam_types"])
    up = sum(1 for s,_ in all_subjects if "UPPSC" in s["exam_types"])
    sc = sum(1 for s,_ in all_subjects if any("SSC" in e for e in s["exam_types"]))
    print(f"""
╔══════════════════════════════════════════════════╗
║  ✅  UttarakhandMockExams Seed Complete!          ║
╠══════════════════════════════════════════════════╣
║  Subjects : {n} (UK:{uk} UP:{up} SSC:{sc})
║  Sets     : {total_sets} ({n*5} published)
║  Questions: {total_q:,}
╠══════════════════════════════════════════════════╣
║  Admin  : admin@uttarakhandmockexams.in/admin123  ║
║  Demo   : rahul@example.com / demo123             ║
╠══════════════════════════════════════════════════╣
║  Run: python3 server.py → http://localhost:5000   ║
╚══════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    seed()
