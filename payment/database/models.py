from database.connection import get_db

class Payment:
    @staticmethod
    def create_payment(account_id, amount, billing_ids, status="PROCESSING"):
        """Create a new payment record."""
        conn = get_db()
        try:
            cursor = conn.execute(
                '''
                INSERT INTO payments (account_id, amount, billing_ids, status)
                VALUES (?, ?, ?, ?)
                ''',
                (account_id, amount, ", ".join(str(id) for id in billing_ids), status)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_payment_by_id(payment_id):
        """Get payment by ID."""
        conn = get_db()
        try:
            row = conn.execute(
                'SELECT * FROM payments WHERE id = ?',
                (payment_id,)
            ).fetchone()
            return row
        finally:
            conn.close()

    @staticmethod
    def update_payment_status(payment_id, new_status):
        """Update payment status."""
        conn = get_db()
        try:
            conn.execute(
                'UPDATE payments SET status = ? WHERE id = ?',
                (new_status, payment_id)
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_payments_by_account(account_id):
        """Get all payments for a specific account."""
        conn = get_db()
        try:
            rows = conn.execute(
                'SELECT * FROM payments WHERE account_id = ?',
                (account_id,)
            ).fetchall()
            return rows
        finally:
            conn.close()

    @staticmethod
    def to_dict(row):
        """Convert database row to dict."""
        if row is None:
            return None
        return {
            'id': row['id'],
            'account_id': row['account_id'],
            'billing_ids': [int(id) for id in row['billing_ids'].split(',')],
            'amount': row['amount'],
            'status': row['status'],
            'created_at': row['created_at']
        }
