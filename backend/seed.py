"""
UttarakhandMockExams — Seed Script
Populates DB: 8 subjects × 30 daily sets × 30 questions = 7,200 questions
Run: python3 seed.py
"""

import sys, os, json, uuid, time
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("DB_PATH", "./uttarakhandmockexams.db")

from database import init_db, get_conn
from auth_utils import hash_password
from seed_data import SUBJECTS, QUESTIONS

def seed():
    print("\n🌱  Seeding UttarakhandMockExams database...\n")
    init_db()
    conn = get_conn()

    # Wipe existing data
    conn.executescript("""
        DELETE FROM attempt_answers;
        DELETE FROM exam_attempts;
        DELETE FROM user_progress;
        DELETE FROM pdf_uploads;
        DELETE FROM questions;
        DELETE FROM daily_sets;
        DELETE FROM subjects;
        DELETE FROM users;
    """)
    conn.commit()

    # ── Seed Subjects ──────────────────────────────────────────────────────────
    subject_ids = {}
    for s in SUBJECTS:
        cur = conn.execute(
            "INSERT INTO subjects (name,name_hindi,icon,color_class,exam_types,sort_order) VALUES (?,?,?,?,?,?)",
            (s["name"],
             s.get("name_hindi", ""),
             s.get("icon", ""),
             s.get("color_class", ""),
             json.dumps(s.get("exam_types", [])),
             s.get("sort_order", 0))
        )
        subject_ids[s["name"]] = cur.lastrowid
        print(f"  ✓  Subject: {s['icon']}  {s['name']}  (id={cur.lastrowid})")
    conn.commit()

    # ── Seed Sets + Questions ──────────────────────────────────────────────────
    total_sets = 0
    total_questions = 0

    for subj in SUBJECTS:
        sid = subject_ids[subj["name"]]
        exam_types_json = json.dumps(subj["exam_types"])
        bank = QUESTIONS.get(subj["name"], [])

        for day in range(1, 31):
            from datetime import date, timedelta
            sched = (date(2026, 3, 1) + timedelta(days=day-1)).isoformat()
            # First 3 days published; rest unpublished (admin publishes via panel)
            published = 1 if day <= 3 else 0

            set_row = conn.execute(
                "INSERT INTO daily_sets (subject_id,day_number,title,title_hindi,exam_types,"
                "scheduled_date,total_questions,is_published) VALUES (?,?,?,?,?,?,30,?)",
                (sid, day,
                 f"{subj['name']} — Day {day} Mock Test",
                 f"{subj['name']} — दिन {day} मॉक टेस्ट",
                 exam_types_json, sched, published)
            )
            set_id = set_row.lastrowid
            total_sets += 1

            for qn in range(1, 31):
                if bank:
                    tpl = bank[(qn - 1) % len(bank)]
                    conn.execute(
                        "INSERT INTO questions (set_id,q_number,question_en,question_hi,"
                        "option_a_en,option_b_en,option_c_en,option_d_en,"
                        "correct_ans,explanation,difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (set_id, qn, tpl["qe"], tpl.get("qh"),
                         tpl["opts"][0], tpl["opts"][1], tpl["opts"][2], tpl["opts"][3],
                         tpl["ans"], tpl.get("exp",""), tpl.get("diff","medium"))
                    )
                else:
                    conn.execute(
                        "INSERT INTO questions (set_id,q_number,question_en,correct_ans,"
                        "option_a_en,option_b_en,option_c_en,option_d_en) VALUES (?,?,?,?,?,?,?,?)",
                        (set_id, qn,
                         f"{subj['name']} Q{qn} — Upload PDF to replace with real question",
                         qn % 4, "Option A", "Option B", "Option C", "Option D")
                    )
                total_questions += 1

        conn.commit()
        print(f"  ✓  {subj['icon']}  {subj['name']}: 30 sets × 30 questions seeded")

    # ── Admin User ─────────────────────────────────────────────────────────────
    admin_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO users (id,name,email,password,role) VALUES (?,?,?,?,'admin')",
        (admin_id, "Admin", "admin@uttarakhandmockexams.in", hash_password("admin123"))
    )

    # ── Demo Student ───────────────────────────────────────────────────────────
    student_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO users (id,name,email,phone,password,role,exam_target) VALUES (?,?,?,?,?,'student','SSC')",
        (student_id, "Rahul Sharma", "rahul@example.com", "9876543210", hash_password("student123"))
    )
    conn.commit()
    conn.close()

    sub_count = len(SUBJECTS)
    print(f"""
✅  Seed complete!
    Subjects    : {sub_count}
    Daily Sets  : {total_sets}  ({sub_count * 3} published, rest pending)
    Questions   : {total_questions:,}

👤  Admin user     : admin@uttarakhandmockexams.in  /  admin123
👤  Student user   : rahul@example.com     /  student123

🚀  Start server   : python3 server.py
📡  API base URL   : http://localhost:5000/api
""")

if __name__ == "__main__":
    seed()
