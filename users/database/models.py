from database.connection import get_db

class User:
    @staticmethod
    def get_user_by_email(email):
        """Get user by email."""
        conn = get_db()
        try:
            cursor = conn.execute(
                'SELECT * FROM users WHERE email = ?',
                (email,)
            )
            row = cursor.fetchone()
            return User.to_dict(row)
        finally:
            conn.close()

    @staticmethod
    def get_user_by_credentials(email, password):
        """Get user by credentials."""
        conn = get_db()
        try:
            cursor = conn.execute(
                'SELECT * FROM users WHERE email = ? AND password = ?',
                (email, password)
            )
            row = cursor.fetchone()
            return User.to_dict(row)
        finally:
            conn.close()

    @staticmethod
    def create_user(email, name, description, password, sex):
        """Create a new user record."""
        conn = get_db()
        try:
            cursor = conn.execute(
                '''
                INSERT INTO users (email, description, username, password, name, sex)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (email, description, email, password, name, sex)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID."""
        conn = get_db()
        try:
            cursor = conn.execute(
                'SELECT * FROM users WHERE id = ?',
                (user_id,)
            )
            row = cursor.fetchone()
            return User.to_dict(row)
        finally:
            conn.close()

    @staticmethod
    def to_dict(row):
        """Convert database row to dict."""
        if row is None:
            return None
        return {
            'id': row['id'],
            'email': row['email'],
            'username': row['username'],
            'description': row['description'],
            'name': row['name'],
            'sex': row['sex'],
            'is_admin': row['is_admin'],
        }
