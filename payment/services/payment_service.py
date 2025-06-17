from database.models import Payment
from monitoring.logger import log_database_operation, log_business_event
import time

class PaymentService:
    @staticmethod
    def create_payment(account_id, billing_ids, amount):
        try:
            if not billing_ids:
                raise ValueError("Billing IDs are required")
            if account_id is None:
                raise ValueError("Account ID is required")
            if amount is None:
                raise ValueError("Amount is required")
            if not isinstance(billing_ids, list):
                raise ValueError("Billing IDs must be a list")
            if amount <= 0:
                raise ValueError("Amount must be positive")
            if not isinstance(amount, (int, float)):
                raise ValueError("Amount must be a number")

            amount = float(amount)

            payment_id = Payment.create_payment(account_id, amount, billing_ids, 'PROCESSING')
            log_database_operation("Create payment", payment_id=payment_id, account_id=account_id, amount=amount, billing_ids=billing_ids)

            time.sleep(2)

            Payment.update_payment_status(payment_id, 'COMPLETED')
            log_database_operation("Update payment status", payment_id=payment_id, status='COMPLETED')

            log_business_event("Payment completed", payment_id=payment_id)

            return payment_id
        except Exception as e:
            print(f"Error creating payment: {e}")

    @staticmethod
    def get_payments_by_account(account_id):
        try:
            if not account_id:
                raise ValueError("Account ID is required")

            rows = Payment.get_payments_by_account(account_id)
            payments = [Payment.to_dict(row) for row in rows]

            log_database_operation("Get payments by account", account_id=account_id, count=len(payments))

            return payments
        except Exception as e:
            print(f"Error retrieving payments: {e}")
