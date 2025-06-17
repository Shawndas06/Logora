from collections import defaultdict

def transform_bills(bills):
    """Transform bills data to include service totals and overall total."""
    service_totals = defaultdict(float)
    total_amount = 0
    
    for bill in bills:
        service_type = bill['type']
        amount = bill['amount']
        service_totals[service_type] += amount
        total_amount += amount
    
    total_services = [
        {'type': service_type, 'amount': amount} 
        for service_type, amount in service_totals.items()
    ]
    
    return {
        'services': bills,
        'total': {
            'services': total_services,
            'amount': total_amount
        }
    }
