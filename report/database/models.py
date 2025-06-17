from database.connection import get_db
from datetime import datetime


class Account:
    def __init__(self, row):
        self.id = row['id']
        self.number = row['number']
        self.address = row['address']
        self.area = row['area']
        self.residents = row['residents']
        self.management_company = row['management_company']
        self.created_at = row['created_at']
        self.updated_at = row['updated_at']

    @staticmethod
    def get_by_id(account_id):
        """Get account by ID."""
        conn = get_db()
        try:
            query = "SELECT * FROM accounts WHERE id = ?"
            row = conn.execute(query, (account_id,)).fetchone()
            return Account(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def create(number, address, area, residents, management_company):
        """Create a new account."""
        conn = get_db()
        try:
            query = """
            INSERT INTO accounts (number, address, area, residents, management_company)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor = conn.execute(query, (number, address, area, residents, management_company))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()


class Charge:
    def __init__(self, row):
        self.id = row['id']
        self.account_id = row['account_id']
        self.service_type = row['service_type']
        self.amount = row['amount']
        self.period_start = row['period_start']
        self.period_end = row['period_end']
        self.created_at = row['created_at']

    @staticmethod
    def get_by_account_id(account_id):
        """Get all charges for an account."""
        conn = get_db()
        try:
            query = "SELECT * FROM charges WHERE account_id = ? ORDER BY period_start DESC"
            rows = conn.execute(query, (account_id,)).fetchall()
            return [Charge(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def create(account_id, service_type, amount, period_start, period_end):
        """Create a new charge."""
        conn = get_db()
        try:
            query = """
            INSERT INTO charges (account_id, service_type, amount, period_start, period_end)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor = conn.execute(query, (account_id, service_type, amount, period_start, period_end))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()


class Payment:
    def __init__(self, row):
        self.id = row['id']
        self.account_id = row['account_id']
        self.payment_date = row['payment_date']
        self.amount = row['amount']
        self.method = row['method']
        self.created_at = row['created_at']

    @staticmethod
    def get_by_account_id(account_id):
        """Get all payments for an account."""
        conn = get_db()
        try:
            query = "SELECT * FROM payments WHERE account_id = ? ORDER BY payment_date DESC"
            rows = conn.execute(query, (account_id,)).fetchall()
            return [Payment(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def create(account_id, payment_date, amount, method):
        """Create a new payment."""
        conn = get_db()
        try:
            query = """
            INSERT INTO payments (account_id, payment_date, amount, method)
            VALUES (?, ?, ?, ?)
            """
            cursor = conn.execute(query, (account_id, payment_date, amount, method))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()


class Report:
    def __init__(self, row):
        self.id = row['id']
        self.account_id = row['account_id']
        self.period_start = row['period_start']
        self.period_end = row['period_end']
        self.total_amount = row['total_amount']
        self.services_data = row['services_data']
        self.qr_data = row['qr_data']
        self.file_path = row['file_path']
        self.status = row['status']
        self.created_at = row['created_at']
        self.updated_at = row['updated_at']

    @staticmethod
    def get_by_id(report_id):
        """Get a specific report by ID."""
        conn = get_db()
        try:
            query = "SELECT * FROM reports WHERE id = ?"
            row = conn.execute(query, (report_id,)).fetchone()
            return Report(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_by_account_id(account_id):
        """Get all reports for an account."""
        conn = get_db()
        try:
            query = "SELECT * FROM reports WHERE account_id = ? ORDER BY created_at DESC"
            rows = conn.execute(query, (account_id,)).fetchall()
            return [Report(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def create(account_id, period_start, period_end, total_amount, services_data, qr_data, file_path):
        """Create a new report."""
        conn = get_db()
        try:
            query = """
            INSERT INTO reports (account_id, period_start, period_end, total_amount, 
                               services_data, qr_data, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor = conn.execute(query, (
                account_id, period_start, period_end, total_amount,
                services_data, qr_data, file_path
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def update_status(report_id, status):
        """Update report status."""
        conn = get_db()
        try:
            query = """
            UPDATE reports 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            conn.execute(query, (status, report_id))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def get_reports_by_type(report_type, period_months=None):
        """Get reports by type within a period."""
        conn = get_db()
        try:
            if period_months:
                query = """
                SELECT * FROM reports 
                WHERE report_type = ? 
                AND created_at >= date("now", "-{} months")
                ORDER BY created_at DESC
                """.format(
                    period_months
                )
                rows = conn.execute(query, (report_type,)).fetchall()
            else:
                query = """
                SELECT * FROM reports 
                WHERE report_type = ?
                ORDER BY created_at DESC
                """
                rows = conn.execute(query, (report_type,)).fetchall()
            return rows
        finally:
            conn.close()

    @staticmethod
    def get_all_reports(limit=50):
        """Get all reports with optional limit."""
        conn = get_db()
        try:
            query = """
            SELECT * FROM reports 
            ORDER BY created_at DESC 
            LIMIT ?
            """
            rows = conn.execute(query, (limit,)).fetchall()
            return rows
        finally:
            conn.close()

    @staticmethod
    def create_report(report_type, title, data, status="pending"):
        """Create a new report record."""
        conn = get_db()
        try:
            conn.execute(
                """
            INSERT INTO reports (report_type, title, data, status)
            VALUES (?, ?, ?, ?)
            """,
                (report_type, title, data, status),
            )
            conn.commit()
            return conn.lastrowid
        finally:
            conn.close()

    @staticmethod
    def update_report_status(report_id, status, pdf_path=None):
        """Update report status and optionally PDF path."""
        conn = get_db()
        try:
            if pdf_path:
                conn.execute(
                    """
                UPDATE reports 
                SET status = ?, pdf_path = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                    (status, pdf_path, report_id),
                )
            else:
                conn.execute(
                    """
                UPDATE reports 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                    (status, report_id),
                )
            conn.commit()
            return conn.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def delete_report(report_id):
        """Delete a report by ID."""
        conn = get_db()
        try:
            conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))
            conn.commit()
            return conn.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def to_dict(row):
        """Convert database row to dictionary."""
        return {
            "id": row["id"],
            "reportType": row["report_type"],
            "title": row["title"],
            "data": row["data"],
            "status": row["status"],
            "pdfPath": row["pdf_path"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
        }
