from flask import Blueprint, jsonify, current_app
import requests
from external_api_client import fetch_odds_data

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

@api_bp.route('/getodds', methods=['GET'])
def get_odds(sport, region, markets):
    """Placeholder call to external api to retrieve odds"""
    if not sport:
        return jsonify({"error": "Sport cannot be null"}), 400
    try:
        data = fetch_odds_data(sport, region, markets)
        return jsonify([data]), 200
    except:
        return jsonify({"error": "Failed to get odds data"}), 500


    