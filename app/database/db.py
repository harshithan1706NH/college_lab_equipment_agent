import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "lab_equipment.db"
)


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection




def initialize_database():
    connection = get_db_connection()
    cursor = connection.cursor()

   

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL
        )
    """)


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

            FOREIGN KEY (user_id)
                REFERENCES users(id),

            FOREIGN KEY (equipment_id)
                REFERENCES equipment(id)
        )
    """)

    

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()



def seed_database():
    connection = get_db_connection()
    cursor = connection.cursor()



    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    if user_count > 0:
        connection.close()
        return

 

    users = [
        (
            "Harshitha",
            "harshitha@example.com",
            "student"
        ),
        (
            "Vicky",
            "vicky@example.com",
            "student"
        ),
        (
            "Hoshi",
            "hoshi@example.com",
            "student"
        )
    ]

    cursor.executemany("""
        INSERT INTO users (
            name,
            email,
            role
        )
        VALUES (?, ?, ?)
    """, users)

  

    equipment = [

       
        (
            "Oscilloscope",
            "Measurement",
            "Electronics Lab",
            10,
            8,
            "Working"
        ),

        (
            "Digital Multimeter",
            "Measurement",
            "Electronics Lab",
            12,
            10,
            "Working"
        ),

        (
            "Function Generator",
            "Signal",
            "Electronics Lab",
            6,
            4,
            "Working"
        ),

        (
            "DC Power Supply",
            "Power",
            "Electronics Lab",
            8,
            8,
            "Working"
        ),

        (
            "Soldering Iron",
            "Tools",
            "Electronics Lab",
            15,
            13,
            "Working"
        ),

       

        (
            "Digital Logic Trainer",
            "Training Kit",
            "Digital Electronics Lab",
            8,
            6,
            "Working"
        ),

        (
            "Logic Analyzer",
            "Measurement",
            "Digital Electronics Lab",
            5,
            4,
            "Working"
        ),

        (
            "FPGA Development Board",
            "Development Board",
            "Digital Electronics Lab",
            10,
            9,
            "Working"
        ),

        (
            "IC Tester",
            "Testing",
            "Digital Electronics Lab",
            4,
            4,
            "Working"
        ),

        (
            "Breadboard",
            "Prototype Board",
            "Digital Electronics Lab",
            20,
            18,
            "Working"
        ),

        

        (
            "Spectrum Analyzer",
            "Measurement",
            "Communication Lab",
            3,
            2,
            "Working"
        ),

        (
            "RF Signal Generator",
            "Signal",
            "Communication Lab",
            4,
            3,
            "Working"
        ),

        (
            "Antenna Trainer",
            "Training Kit",
            "Communication Lab",
            6,
            5,
            "Working"
        ),

        (
            "CRO",
            "Measurement",
            "Communication Lab",
            5,
            5,
            "Working"
        ),

        (
            "Communication Trainer Kit",
            "Training Kit",
            "Communication Lab",
            7,
            5,
            "Working"
        )
    ]

    cursor.executemany("""
        INSERT INTO equipment (
            name,
            category,
            lab,
            quantity,
            available_quantity,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, equipment)

    connection.commit()
    connection.close()