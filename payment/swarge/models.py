from flask_restx import fields

payment_model = {
    'id': fields.Integer(required=True, description='Payment ID'),
    'account_id': fields.Integer(required=True, description='Account ID'),
    'amount': fields.Float(required=True, description='Payment amount'),
    'status': fields.String(required=True, description='Payment status', enum=['PROCESSING', 'COMPLETED']),
    'created_at': fields.DateTime(required=True, description='Creation timestamp')
}

payment_create_request_model = {
    'account_id': fields.Integer(required=True, description='Account ID'),
    'amount': fields.Float(required=True, description='Payment amount', min=0.01)
}

payment_response_model = {
    'success': fields.Boolean(required=True, description='Operation status'),
    'data': fields.Nested(payment_model, description='Payment data'),
    'message': fields.String(description='Optional message or error')
}

payment_create_response_model = {
    'success': fields.Boolean(required=True, description='Operation status'),
    'data': fields.Raw(description='Payment ID'),
    'message': fields.String(description='Optional message or error')
}
