import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        otp INTEGER,
        image BLOB,
        password TEXT NOT NULL
        
    )
""")
conn.commit()
conn.close()

def add_user(name,email,age,gender, otp,image,password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        # Read the image file as a binary stream
        if image is not None:
            image = image.read()
            c.execute("INSERT INTO users (name,email,age,gender,otp,image,password) VALUES (?, ?, ?,?,?,?,?)", (name,email,age,gender,otp,image,password))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False    
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()
    return user
def fetch_user(email):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user
def update_otp(email, otp):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET otp = ? WHERE email = ?", (otp, email))
    conn.commit()
    conn.close()
def fetch_otp(email):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT otp FROM users WHERE email = ?", (email,))
    otp = c.fetchone()
    conn.close()
    return otp[0] if otp else None
