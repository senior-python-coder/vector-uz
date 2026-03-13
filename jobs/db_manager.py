import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta


class Database:
    def __init__(self, name_db="Users.db"):
        self.name_db = name_db
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.name_db)

    def _create_table(self):
        conn = self._connect()
        cur = conn.cursor()
        # Users jadvali + xato urinishlar uchun ustunlar
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,       
            failed_attempts INTEGER DEFAULT 0,
            last_attempt TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        conn.close()

    # --- Ro'yxatdan o'tish ---
    def register(self, username, email, password):
        if len(password) < 8:
            return False, "Parol kamida 8 belgidan iborat bo'lishi kerak!"

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (username, email, hashed_password))
            conn.commit()
            return True, "Ro'yxatdan muvaffaqiyatli o'tdingiz!"
        except sqlite3.IntegrityError:
            return False, "Username yoki email mavjud!"
        finally:
            conn.close()

    # --- Kirish (email + password) ---
    def sign_in(self, email, password):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, username, password, failed_attempts, last_attempt 
            FROM users WHERE email=?
        """, (email,))
        user = cur.fetchone()

        if not user:
            conn.close()
            return False, "Email yoki parol xato!"  # xato xabar umumiy bo‘lsin

        user_id, username, stored_hash, failed_attempts, last_attempt = user

        # Brute-force himoya: agar 5 marta xato bo‘lsa 5 daqiqa kutish
        if failed_attempts >= 5:
            if last_attempt:
                last_attempt_time = datetime.strptime(last_attempt, "%Y-%m-%d %H:%M:%S.%f")
                if datetime.now() - last_attempt_time < timedelta(minutes=5):
                    conn.close()
                    return False, "Ko‘p marta xato parol kiritdingiz, 5 daqiqa kuting!"
            # 5 daqiqadan oshgan bo‘lsa counterni reset qilamiz
            cur.execute("UPDATE users SET failed_attempts=0 WHERE id=?", (user_id,))
            conn.commit()

        # Parolni tekshirish
        if check_password_hash(stored_hash, password):
            # Muvaffaqiyatli login → failed_attempts ni reset
            cur.execute("UPDATE users SET failed_attempts=0, last_attempt=NULL WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
            return True, f"Xush kelibsiz, {username}!"
        else:
            # Xato parol → failed_attempts +1 va last_attempt yangilash
            cur.execute("UPDATE users SET failed_attempts = failed_attempts + 1, last_attempt=? WHERE id=?",
                        (datetime.now(), user_id))
            conn.commit()
            conn.close()
            return False, "Email yoki parol xato!"  # umumiy xato xabar