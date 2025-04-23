import hashlib
from datetime import datetime

class AuthController:
    def __init__(self, db):
        self.db = db

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password, role):
        hashed_password = self.hash_password(password)
        try:
            self.db.execute(
                "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                (username, hashed_password, role, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
        except Exception as e:
            raise Exception(f"Error registering user: {e}")

    def login(self, username, password):
        hashed_password = self.hash_password(password)
        user = self.db.fetchone(
            "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        if user:
            return {"id": user[0], "username": user[1], "role": user[2]}
        return None