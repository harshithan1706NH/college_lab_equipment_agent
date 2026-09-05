import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent.parent / "lab_equipment.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Equipment
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            lab TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            available_quantity INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'Working'
        )
    """)

    # Borrowing records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS borrowings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            equipment_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            borrow_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT NOT NULL DEFAULT 'Borrowed',

            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (equipment_id) REFERENCES equipment(id)
        )
    """)

    # Notifications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()


def seed_database():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Add a test user if none exists
    cursor.execute("SELECT COUNT(*) FROM users")

    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (name, email, role)
            VALUES (?, ?, ?)
        """, (
            "Harshitha",
            "harshitha@example.com",
            "student"
        ))

    # Add sample equipment if none exists
    cursor.execute("SELECT COUNT(*) FROM equipment")

    if cursor.fetchone()[0] == 0:
        equipment = [
            ("Oscilloscope", "Measurement", "Electronics Lab", 10, 10, "Working"),
            ("Multimeter", "Measurement", "Electronics Lab", 8, 8, "Working"),
            ("Function Generator", "Signal", "Electronics Lab", 5, 5, "Working"),
            ("Soldering Iron", "Tools", "Electronics Lab", 12, 12, "Working"),
            ("Digital Logic Trainer", "Training Kit", "Digital Lab", 6, 6, "Working")
        ]

        cursor.executemany("""
            INSERT INTO equipment
            (name, category, lab, quantity, available_quantity, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, equipment)

    connection.commit()
    connection.close()