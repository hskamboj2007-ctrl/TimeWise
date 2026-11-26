"""
TimeWise - Database Manager (SQLite)
Handles persistent storage for tasks, daily plans, and weekly/monthly completion analytics.
"""

import sqlite3
import os
from datetime import datetime, timedelta, date

DB_FILE = "timewise.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tasks Table with deadline_date
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        duration INTEGER NOT NULL,              -- in minutes
        priority TEXT NOT NULL,                 -- High, Medium, Low
        has_deadline INTEGER NOT NULL,          -- 1 or 0
        deadline_date TEXT,                     -- YYYY-MM-DD
        status TEXT NOT NULL DEFAULT 'Pending', -- Pending, Completed
        scheduled_start TEXT,                   -- e.g. '10:00 AM'
        scheduled_end TEXT,                     -- e.g. '11:00 AM'
        category TEXT DEFAULT 'Study',
        completed_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Available Work Time Table (singleton row)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        day_start_time TEXT DEFAULT '09:00',
        available_minutes INTEGER DEFAULT 240 -- 4 hours default
    )
    """)

    # Weekly & Monthly History Table for line chart analysis
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS completion_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_str TEXT NOT NULL UNIQUE,       -- YYYY-MM-DD
        day_name TEXT NOT NULL,              -- Mon, Tue, etc.
        completed_count INTEGER DEFAULT 0,
        total_count INTEGER DEFAULT 0,
        focus_minutes INTEGER DEFAULT 0
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (id, day_start_time, available_minutes) VALUES (1, '09:00', 360)")

    # Seed initial tasks matching user's screenshot
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        today_str = date.today().strftime("%Y-%m-%d")
        tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        next_week_str = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")

        sample_tasks = [
            ("Machine Learning", 90, "High", 1, today_str, "Pending", "10:00 AM", "11:30 AM", "Study"),
            ("DBMS Assignment", 60, "Medium", 1, tomorrow_str, "Pending", "12:00 PM", "01:00 PM", "Assignment"),
            ("Project Work", 120, "Low", 1, next_week_str, "Pending", "04:00 PM", "06:00 PM", "Project"),
            ("Algorithm Practice", 45, "High", 1, today_str, "Completed", "02:00 PM", "02:45 PM", "Coding"),
            ("Read Research Paper", 30, "Medium", 0, None, "Completed", "03:00 PM", "03:30 PM", "Reading"),
            ("System Design Revision", 45, "High", 1, tomorrow_str, "Completed", "05:00 PM", "05:45 PM", "Study"),
            ("Review Pull Requests", 20, "Low", 0, None, "Completed", "06:00 PM", "06:20 PM", "Work"),
            ("Daily Notes Journaling", 15, "Low", 0, None, "Completed", "06:30 PM", "06:45 PM", "Personal")
        ]
        cursor.executemany("""
            INSERT INTO tasks (title, duration, priority, has_deadline, deadline_date, status, scheduled_start, scheduled_end, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_tasks)

    cursor.execute("SELECT COUNT(*) FROM completion_history")
    if cursor.fetchone()[0] == 0:
        today = datetime.now()
        days_seed = [
            ("Mon", 4, 6, 180),
            ("Tue", 6, 7, 240),
            ("Wed", 5, 8, 210),
            ("Thu", 7, 8, 270),
            ("Fri", 5, 6, 200),
            ("Sat", 3, 5, 120),
            ("Sun", 5, 8, 220),
        ]
        for i, (day, comp, tot, focus) in enumerate(days_seed):
            target_date = (today - timedelta(days=(6 - i))).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT OR IGNORE INTO completion_history (date_str, day_name, completed_count, total_count, focus_minutes)
                VALUES (?, ?, ?, ?, ?)
            """, (target_date, day, comp, tot, focus))

    conn.commit()
    conn.close()

def get_all_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY status ASC, CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, id ASC")
    rows = cursor.fetchall()
    tasks = [dict(row) for row in rows]
    conn.close()
    return tasks

def add_task(title, duration, priority, has_deadline, deadline_date, category="Study"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, duration, priority, has_deadline, deadline_date, status, category)
        VALUES (?, ?, ?, ?, ?, 'Pending', ?)
    """, (title, duration, priority, 1 if has_deadline else 0, deadline_date if has_deadline else None, category))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def toggle_task_status(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    current_status = row["status"]
    new_status = "Completed" if current_status == "Pending" else "Pending"
    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if new_status == "Completed" else None

    cursor.execute("UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?", (new_status, completed_at, task_id))
    conn.commit()
    conn.close()
    return new_status

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def update_task_schedule(task_id, start_str, end_str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET scheduled_start = ?, scheduled_end = ? WHERE id = ?", (start_str, end_str, task_id))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM tasks")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as completed FROM tasks WHERE status = 'Completed'")
    completed = cursor.fetchone()["completed"]
    pending = total - completed
    progress = round((completed / total * 100)) if total > 0 else 0

    if total == 0:
        plant_stage = 0
        stage_name = "Ready to Plant"
        plant_desc = "Add tasks to plant your productivity seed!"
    elif completed == 0:
        plant_stage = 0
        stage_name = "Seed in Soil"
        plant_desc = "Complete your first task to sprout the seed!"
    elif progress < 25:
        plant_stage = 1
        stage_name = "Sprout"
        plant_desc = "Great start! A small green sprout has emerged 🌱"
    elif progress < 50:
        plant_stage = 2
        stage_name = "Seedling"
        plant_desc = "Growing strong! Two fresh green leaves are unfolding 🌿"
    elif progress < 75:
        plant_stage = 3
        stage_name = "Vegetative"
        plant_desc = "Your productivity is flourishing with lush stems 🍃"
    elif progress < 100:
        plant_stage = 4
        stage_name = "Budding Flower"
        plant_desc = "Almost there! Flower buds are preparing to bloom 🌸"
    else:
        plant_stage = 5
        stage_name = "Fully Bloomed!"
        plant_desc = "Outstanding! All tasks completed, your plant is in full bloom 🌺✨"

    conn.close()
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "progress": progress,
        "plant_stage": plant_stage,
        "stage_name": stage_name,
        "plant_desc": plant_desc
    }

def get_settings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT day_start_time, available_minutes FROM settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"day_start_time": row["day_start_time"], "available_minutes": row["available_minutes"]}
    return {"day_start_time": "09:00", "available_minutes": 360}

def update_settings(day_start_time, available_minutes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET day_start_time = ?, available_minutes = ? WHERE id = 1", (day_start_time, available_minutes))
    conn.commit()
    conn.close()

def get_history_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM completion_history ORDER BY date_str ASC")
    rows = cursor.fetchall()
    weekly = [dict(r) for r in rows]

    monthly = [
        {"label": "Week 1", "completed": 24, "total": 32, "rate": 75},
        {"label": "Week 2", "completed": 28, "total": 35, "rate": 80},
        {"label": "Week 3", "completed": 31, "total": 36, "rate": 86},
        {"label": "Week 4", "completed": 35, "total": 40, "rate": 88}
    ]
    conn.close()
    return {"weekly": weekly, "monthly": monthly}

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully with deadline_date support.")
