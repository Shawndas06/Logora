from collections import defaultdict

def transform_payments(payments):
    """Aggregate payments by status and compute total amount."""
    status_totals = defaultdict(float)
    total_amount = 0
    
    for payment in payments:
        status = payment['status']
        amount = payment['amount']
        status_totals[status] += amount
        total_amount += amount
    
    total_by_status = [
        {'status': status, 'amount': amount}
        for status, amount in status_totals.items()
    ]
    
    return {
        'payments': payments,
        'total': {
            'by_status': total_by_status,
            'amount': total_amount
        }
    }
