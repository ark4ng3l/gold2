import bcrypt
import datetime

class UserModel:
    def __init__(self, db):
        """Initialize the user model with a database connection."""
        self.db = db

    def register(self, username, password, role):
        """Register a new user."""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        created_at = datetime.datetime.now().isoformat()
        try:
            self.db.execute(
                "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                (username, hashed_password, role, created_at)
            )
            return True
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise Exception("نام کاربری قبلاً ثبت شده است")
            raise e

    def login(self, username, password):
        """Authenticate a user."""
        user = self.db.fetchone("SELECT * FROM users WHERE username = ?", (username,))
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return {'id': user[0], 'username': user[1], 'role': user[3]}
        return None