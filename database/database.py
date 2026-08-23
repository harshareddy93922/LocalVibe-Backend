import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "localvibe.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            destination TEXT,
            people TEXT,
            dates TEXT,
            message TEXT NOT NULL,
            interest TEXT,
            status TEXT NOT NULL DEFAULT 'NEW',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_enquiry(data):
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO enquiries
        (name, phone, email, destination, people, dates, message, interest)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"], data["phone"], data.get("email"), data.get("destination"),
        data.get("people"), data.get("dates"), data["message"], data.get("interest")
    ))
    conn.commit()
    item_id = cur.lastrowid
    conn.close()
    return item_id

def list_enquiries():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM enquiries ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_status(item_id, status):
    conn = get_connection()
    conn.execute("UPDATE enquiries SET status=? WHERE id=?", (status, item_id))
    conn.commit()
    conn.close()
