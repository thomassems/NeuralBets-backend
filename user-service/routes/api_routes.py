from flask import Blueprint, jsonify

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

@api_bp.route('/status', methods=['GET'])
def api_status():
    """Returns the status of the sub-API service."""
    return jsonify({
        "status": "online",
        "version": "1.0",
        "service_area": "Modular API Blueprint"
    }), 200

@api_bp.route('/users', methods=['GET'])
def list_users():
    """Placeholder endpoint for managing user resources."""
    # In a real application, this would query the database
    return jsonify([
        {"id": 1, "username": "jane_doe"},
        {"id": 2, "username": "john_smith"}
    ]), 200