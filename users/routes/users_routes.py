from flask import Blueprint, request, jsonify
from services.users_service import UsersService

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        email = data.get('email')
        description = data.get('description', '')
        name = data.get('name', '')
        sex = data.get('sex')
        password = data.get('password')

        user_id = UsersService.create_user(email, name, sex, description, password)

        return jsonify({
            "success": True,
            "data": { "id": user_id },
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    except Exception:
        return jsonify({"success": False, "message": "Internal server error"}), 500

@users_bp.route('/api/users', methods=['GET'])
def get_user_by_credentials():
    args = request.args

    email = args.get('email')
    password = args.get('password')

    print("Received credentials:", email, password)

    try:
        user = UsersService.get_user_by_credentials(email, password)

        return jsonify({
            "success": True,
            "data": user
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    except Exception:
        return jsonify({"success": False, "message": "Internal server error"}), 500

@users_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = UsersService.get_user_by_id(user_id)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        return jsonify({
            "success": True,
            "data": user
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    except Exception:
        return jsonify({"success": False, "message": "Internal server error"}), 500
