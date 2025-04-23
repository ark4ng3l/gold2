import bcrypt

class CryptoManager:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(stored_hash: str, provided_password: str) -> bool:
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))