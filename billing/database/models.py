from database.connection import get_db

class Bill:
    @staticmethod
    def get_bills_by_account(account_id, period_months):
        """Get bills for a specific account within a period."""
        conn = get_db()
        try:
            query = '''
            SELECT * FROM bills
            WHERE account_id = ?
            AND created_at >= date("now", "-{} months")
            '''.format(period_months)

            rows = conn.execute(query, (account_id,)).fetchall()
            return rows
        finally:
            conn.close()

    @staticmethod
    def create_bill(account_id, amount, status, bill_type):
        """Create a new bill record."""
        conn = get_db()
        try:
            conn.execute('''
            INSERT INTO bills (account_id, amount, status, type)
            VALUES (?, ?, ?, ?)
            ''', (account_id, amount, status, bill_type))
            conn.commit()
            return conn.lastrowid
        finally:
            conn.close()

    @staticmethod
    def update_bills(billing_ids, status):
        """Update bill"""
        conn = get_db()
        try:
            conn.executemany('''
            UPDATE bills SET status = ?
            WHERE id = ?
            ''', [(status, id) for id in billing_ids])
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def to_dict(row):
        """Convert database row to dictionary."""
        return {
            'id': row['id'],
            'accountId': row['account_id'],
            'createdAt': row['created_at'],
            'status': row['status'],
            'type': row['type'],
            'amount': row['amount'],
        }
