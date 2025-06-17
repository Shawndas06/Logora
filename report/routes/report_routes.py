from flask import Blueprint, request, jsonify
from services.report_service import ReportService

report_bp = Blueprint('reports', __name__)

@report_bp.route('/reports', methods=['POST'])
def generate_report():
    data = request.get_json()
    account_id = data.get('account_id')
    period = data.get('period')

    if not account_id or not period:
        return jsonify(success=False, error="Missing account_id or period"), 400

    try:
        report_data = ReportService.generate_report_data(account_id, period)
        return jsonify(success=True, data=report_data)
    except ValueError as e:
        return jsonify(success=False, error=str(e)), 400
    except Exception as e:
        return jsonify(success=False, error="Internal server error"), 500