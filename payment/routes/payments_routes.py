from flask import Blueprint, current_app, request, jsonify
from services.payment_service import PaymentService
from config import Config
import requests

payment_bp = Blueprint('payments', __name__)

@payment_bp.route('/api/payments', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        account_id = data.get('account_id')
        billing_ids = data.get('billing_ids')
        amount = data.get('amount')

        payment_id = PaymentService.create_payment(account_id, billing_ids, amount)

        try:
            req = requests.put(f"{Config.BILLING_SERVICE_URL}/api/billings/paid", json={
                "billing_ids": billing_ids
            })
        except Exception as e:
            return jsonify({"success": False, "message": "Billing service unavailable"}), 503

        if req.status_code != 200:
            return jsonify({"success": False, "message": "Failed to update billing status"}), 500

        return jsonify({
            "success": True,
            "data": {"id": payment_id}
        }), 201

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    except Exception:
        return jsonify({"success": False, "message": "Internal server error"}), 500

@payment_bp.route('/api/payments/<int:account_id>', methods=['GET'])
def get_payments(account_id):
    try:
        payments = PaymentService.get_payments_by_account(account_id)

        return jsonify({
            "success": True,
            "data": payments
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    except Exception:
        return jsonify({"success": False, "message": "Internal server error"}), 500
