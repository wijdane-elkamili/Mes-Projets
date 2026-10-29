import sqlite3

conn = sqlite3.connect("hospital.db", check_same_thread=False)
c = conn.cursor()

def create_table():
    c.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        age INTEGER,
        gender TEXT,
        department TEXT,
        waiting_time INTEGER,
        priority TEXT
    )
    """)
    conn.commit()

def add_patient(first_name, last_name, age, gender, department, waiting_time, priority):
    c.execute("""
    INSERT INTO patients(first_name, last_name, age, gender, department, waiting_time, priority)
    VALUES (?,?,?,?,?,?,?)
    """, (first_name, last_name, age, gender, department, waiting_time, priority))
    conn.commit()

def get_patients():
    c.execute("SELECT * FROM patients")
    return c.fetchall()

def delete_patient(id):
    c.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()

def delete_all_patients():
    c.execute("DELETE FROM patients")
    conn.commit()