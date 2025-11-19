from flask import Blueprint, jsonify, current_app
import requests

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
def get_odds():
    """Placeholder call to external api to retrieve odds"""
    key = current_app.config.get('EXTERNAL_API_KEY')
    if not key:
        return jsonify({"error": "missing api key"}), 500
    
    url = "https://api.the-odds-api.com/v4/sports/"
    params = {
        "apiKey": key
    }
    resp = requests.get(url, params=params, timeout=5)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return jsonify({"error": "external API error", "details": resp.text}), resp.status_code
    
    return jsonify(resp.json()), 200


    