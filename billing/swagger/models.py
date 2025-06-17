from flask_restx import fields

# Bill model for responses
bill_model = {
    'id': fields.Integer(required=True, description='Bill ID'),
    'accountId': fields.Integer(required=True, description='Account ID'),
    'amount': fields.Float(required=True, description='Bill amount'),
    'status': fields.String(required=True, description='Bill status', 
                           enum=['paid', 'pending', 'overdue', 'cancelled']),
    'type': fields.String(required=True, description='Service type',
                         enum=['hosting', 'domain', 'ssl', 'backup', 'support', 'bandwidth']),
    'createdAt': fields.DateTime(required=True, description='Creation timestamp')
}

# Service total model
service_total_model = {
    'type': fields.String(required=True, description='Service type'),
    'amount': fields.Float(required=True, description='Total amount for service')
}

# Total summary model  
total_model = {
    'services': fields.List(fields.Nested(service_total_model), description='Service totals'),
    'amount': fields.Float(required=True, description='Grand total amount')
}

# Main billing response model
billing_response_model = {
    'services': fields.List(fields.Nested(bill_model), description='List of bills'),
    'total': fields.Nested(total_model, description='Total summary')
}

# API response wrapper
api_response_model = {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'data': fields.Nested(billing_response_model, description='Response data'),
    'message': fields.String(description='Error message if success is false')
}

# Bill creation request model
bill_create_model = {
    'account_id': fields.Integer(required=True, description='Account ID'),
    'amount': fields.Float(required=True, description='Bill amount', min=0.01),
    'status': fields.String(required=True, description='Bill status',
                           enum=['paid', 'pending', 'overdue', 'cancelled']),
    'type': fields.String(required=True, description='Service type',
                         enum=['hosting', 'domain', 'ssl', 'backup', 'support', 'bandwidth'])
}

# Bill creation response
bill_create_response_model = {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'data': fields.Raw(description='Created bill ID'),
    'message': fields.String(description='Error message if success is false')
}

# Error response model
error_response_model = {
    'success': fields.Boolean(required=True, description='Always false for errors'),
    'message': fields.String(required=True, description='Error description')
}

# Health check response
health_response_model = {
    'status': fields.String(required=True, description='Health status'),
    'database': fields.String(description='Database connection status'),
    'uptime': fields.String(description='Application uptime'),
    'memory_usage': fields.String(description='Memory usage'),
    'disk_usage': fields.String(description='Disk usage')
}
