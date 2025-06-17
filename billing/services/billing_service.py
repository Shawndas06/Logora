from database.models import Bill
from utils.transformers import transform_bills

class BillingService:
    @staticmethod
    def get_billing_data(account_id, period):
        """Get billing data for an account within a specific period."""
        if not account_id:
            raise ValueError("Account ID is required")

        if not str(period).isdigit() or int(period) <= 0:
            raise ValueError("Period must be a positive number")

        rows = Bill.get_bills_by_account(account_id, int(period))

        bills = [Bill.to_dict(row) for row in rows]

        return transform_bills(bills)

    @staticmethod
    def create_new_bill(account_id, amount, status, bill_type):
        """Create a new bill."""

        if not all([account_id, amount, status, bill_type]):
            raise ValueError("All fields are required")

        if amount <= 0:
            raise ValueError("Amount must be positive")

        return Bill.create_bill(account_id, amount, status, bill_type)

    @staticmethod
    def update_billing_data(billing_ids):
        """Update billing data."""

        if not billing_ids or len(billing_ids) == 0:
            raise ValueError("Billing IDs are required")

        for billing_id in billing_ids:
            if not str(billing_id).isdigit() or int(billing_id) <= 0:
                raise ValueError("Billing ID must be a positive number")

        return Bill.update_bills(billing_ids, 'paid')
