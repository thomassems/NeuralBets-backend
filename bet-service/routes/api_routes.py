from flask import Blueprint, jsonify

api_bp = Blueprint('api_bp', __name__, url_prefix='/bets')

@api_bp.route('/status', methods=['GET'])
def api_status():
    """Returns the status of the sub-API service."""
    return jsonify({
        "status": "online",
        "version": "1.0",
        "service_area": "Modular API Blueprint"
    }), 200

@api_bp.route('/', methods=['GET'])
def list_bets():
    """Placeholder endpoint for managing bet resources."""
    # In a real application, this would query the database
    return jsonify([
        {"id": 1, "props": ["fight_1", "over_2.5"], "amount": 100, "odds": 1.5},
    ]), 200
