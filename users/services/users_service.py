from database.models import User
from monitoring.logger import log_database_operation, log_business_event

class UsersService:
    @staticmethod
    def hash_password(password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def create_user(email, name, sex, description, password):
        if not email or not email.strip():
            raise ValueError("Email is required")
        if not name or not name.strip():
            raise ValueError("Name is required")
        if not sex:
            raise ValueError("Sex is required")
        if not password:
            raise ValueError("Password is required")
        if not isinstance(email, str) or not isinstance(name, str) or not isinstance(password, str):
            raise ValueError("Email, name, and password must be strings")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if int(sex) not in [0, 1]:
            raise ValueError("Sex must be either 1 (Male) or 0 (Female")

        hashed_password = UsersService.hash_password(password)


        try:
            if User.get_user_by_email(email):
                raise ValueError("User with this email already exists")
            id = User.create_user(email, name, description, hashed_password, sex)
            print("Register user", email, name, description, hashed_password, sex)
            log_database_operation("Create user", id=id, email=email, name=name)
            return id
        except Exception as e:
            print(f"Error creating user: {e}")
            raise

    @staticmethod
    def get_user_by_id(user_id):
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        user = User.get_user_by_id(user_id)

        log_business_event("User retrieved", user_id=user_id)

        if not user:
            raise ValueError("User not found")

        return user
    
    @staticmethod
    def get_user_by_credentials(email, password):
        if not email or not email.strip():
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")
        if not isinstance(email, str) or not isinstance(password, str):
            raise ValueError("Email and password must be strings")

        hashed_password = UsersService.hash_password(password)

        user = User.get_user_by_credentials(email, hashed_password)

        if user:
            return user
        else:
            raise ValueError("Invalid email or password")
