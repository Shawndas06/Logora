from flask import Blueprint, request, jsonify
from services.billing_service import BillingService

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/api/billings/paid', methods=['PUT'])
def update_billing():
    """Update billing data for an account"""
    try:
        data = request.get_json()
        print("D", data);
        if not data:
            raise ValueError("No data provided")

        billing_ids = data.get('billing_ids')

        BillingService.update_billing_data(billing_ids)

        return jsonify({
            "success": True,
            "message": "Billing data updated successfully"
        }), 200

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:
        print(f"Error updating billing data: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500

@billing_bp.route('/api/billings', methods=['GET'])
def get_billing():
    """Get billing data for an account."""
    try:
        args = request.args
        account_id = args.get('account')
        period = args.get('period', 6)

        data = BillingService.get_billing_data(account_id, period)

        return jsonify({
            "success": True,
            "data": data
        }), 200

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception:
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500

@billing_bp.route('/api/billings', methods=['POST'])
def create_bill():
    """Create a new bill."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400

        bill_id = BillingService.create_new_bill(
            data.get('account_id'),
            data.get('amount'),
            data.get('status'),
            data.get('type')
        )

        return jsonify({
            "success": True,
            "data": {"id": bill_id}
        }), 201

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception:
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500
