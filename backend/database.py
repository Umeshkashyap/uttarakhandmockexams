"""
UttarakhandMockExams — Database Layer
SQLite3 with full schema for exam portal
"""
import sqlite3
import os
import json

DB_PATH = os.environ.get("DB_PATH", "./uttarakhandmockexams.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            phone       TEXT,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL DEFAULT 'student',
            exam_target TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            name_hindi  TEXT NOT NULL,
            icon        TEXT NOT NULL,
            color_class TEXT NOT NULL,
            exam_types  TEXT NOT NULL,
            is_active   INTEGER NOT NULL DEFAULT 1,
            sort_order  INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS daily_sets (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id      INTEGER NOT NULL REFERENCES subjects(id),
            day_number      INTEGER NOT NULL,
            title           TEXT NOT NULL,
            title_hindi     TEXT NOT NULL,
            exam_types      TEXT NOT NULL,
            scheduled_date  TEXT,
            total_questions INTEGER NOT NULL DEFAULT 30,
            duration_min    INTEGER NOT NULL DEFAULT 45,
            marking_correct INTEGER NOT NULL DEFAULT 4,
            marking_wrong   INTEGER NOT NULL DEFAULT 1,
            pdf_source      TEXT,
            is_published    INTEGER NOT NULL DEFAULT 0,
            created_by      TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(subject_id, day_number)
        );

        CREATE TABLE IF NOT EXISTS questions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            set_id          INTEGER NOT NULL REFERENCES daily_sets(id) ON DELETE CASCADE,
            q_number        INTEGER NOT NULL,
            question_en     TEXT NOT NULL,
            question_hi     TEXT,
            option_a_en     TEXT NOT NULL,
            option_b_en     TEXT NOT NULL,
            option_c_en     TEXT NOT NULL,
            option_d_en     TEXT NOT NULL,
            option_a_hi     TEXT,
            option_b_hi     TEXT,
            option_c_hi     TEXT,
            option_d_hi     TEXT,
            correct_ans     INTEGER NOT NULL,
            explanation     TEXT,
            explanation_hi  TEXT,
            difficulty      TEXT DEFAULT 'medium',
            tags            TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS exam_attempts (
            id              TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL REFERENCES users(id),
            set_id          INTEGER NOT NULL REFERENCES daily_sets(id),
            started_at      TEXT NOT NULL DEFAULT (datetime('now')),
            submitted_at    TEXT,
            time_taken_sec  INTEGER,
            total_questions INTEGER NOT NULL DEFAULT 30,
            correct         INTEGER NOT NULL DEFAULT 0,
            wrong           INTEGER NOT NULL DEFAULT 0,
            skipped         INTEGER NOT NULL DEFAULT 0,
            score           INTEGER NOT NULL DEFAULT 0,
            max_score       INTEGER NOT NULL DEFAULT 120,
            percentage      REAL NOT NULL DEFAULT 0,
            status          TEXT NOT NULL DEFAULT 'in_progress'
        );

        CREATE TABLE IF NOT EXISTS attempt_answers (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id      TEXT NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
            question_id     INTEGER NOT NULL REFERENCES questions(id),
            q_number        INTEGER NOT NULL,
            selected_ans    INTEGER,
            is_correct      INTEGER,
            is_marked       INTEGER NOT NULL DEFAULT 0,
            time_spent_sec  INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS pdf_uploads (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            filename        TEXT NOT NULL,
            original_name   TEXT NOT NULL,
            subject_id      INTEGER REFERENCES subjects(id),
            exam_types      TEXT,
            day_number      INTEGER,
            scheduled_date  TEXT,
            file_size_kb    INTEGER,
            upload_status   TEXT NOT NULL DEFAULT 'pending',
            extracted_count INTEGER DEFAULT 0,
            error_message   TEXT,
            uploaded_by     TEXT REFERENCES users(id),
            uploaded_at     TEXT NOT NULL DEFAULT (datetime('now')),
            processed_at    TEXT,
            set_id          INTEGER REFERENCES daily_sets(id)
        );

        CREATE TABLE IF NOT EXISTS user_progress (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         TEXT NOT NULL REFERENCES users(id),
            subject_id      INTEGER NOT NULL REFERENCES subjects(id),
            day_number      INTEGER NOT NULL,
            best_score      REAL DEFAULT 0,
            attempts_count  INTEGER DEFAULT 0,
            last_attempted  TEXT,
            UNIQUE(user_id, subject_id, day_number)
        );

        CREATE INDEX IF NOT EXISTS idx_questions_set   ON questions(set_id);
        CREATE INDEX IF NOT EXISTS idx_attempts_user   ON exam_attempts(user_id);
        CREATE INDEX IF NOT EXISTS idx_attempts_set    ON exam_attempts(set_id);
        CREATE INDEX IF NOT EXISTS idx_answers_attempt ON attempt_answers(attempt_id);
        CREATE INDEX IF NOT EXISTS idx_progress_user   ON user_progress(user_id);
        CREATE INDEX IF NOT EXISTS idx_sets_subject    ON daily_sets(subject_id);
    """)
    conn.commit()
    conn.close()
    print("[DB] Schema ready ✓")

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

def rows_to_list(rows):
    return [dict(r) for r in rows]
