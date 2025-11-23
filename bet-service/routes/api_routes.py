from flask import Blueprint, jsonify, current_app
import requests
from external_api_client import fetch_odds_data, fetch_events_data
import shared_utils
from shared_utils import constants
from respository import BetRepository

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
def get_odds(sport, regions, markets):
    """Placeholder call to external api to retrieve odds"""
    # WILL ALSO NEED TO MAKE SURE THE SPORT IS VALID
    if not sport:
        return jsonify({"error": "Sport cannot be null"}), 400
    if regions not in constants.VALID_REGIONS:
        return jsonify({"error": "Invalid region provided"}), 400
    if markets not in constants.VALID_MARKETS:
        return jsonify({"error": "Invalid markets provided"}), 400
    try:
        data = fetch_odds_data(sport, regions, markets)
        return jsonify([data]), 200
    except:
        return jsonify({"error": "Failed to get odds data"}), 500

@api_bp.route('/getdefaultodds', methods=['GET'])
def get_live_odds():
    repo = BetRepository()
    res = repo.get_live_odds()
    print('here are the odds')
    if res:
        return jsonify(res), 200
    try:
        print('odds outdated, fetching new live odds')
        data = fetch_odds_data(sport='upcoming')
        repo.update_live_odds(data)
        return jsonify([data]), 200
    except:
        return jsonify({"error": "Failed to get odds data"}), 500

@api_bp.route('/getevents', methods=['GET'])
def get_events(sport):
    print('getting events for sport: ', sport)
    if not sport:
        return jsonify({"error": "Sport cannot be null"}), 400
    try:
        data = fetch_events_data(sport)
        return jsonify([data]), 200
    except:
        return jsonify({"error": "Failed to get odds data"}), 500

@api_bp.route('/getdefaultevents', methods=['GET'])
def get_default_events():
    """Gets default events for mma"""
    print('getting default events')
    try:
        data = fetch_events_data("mma_mixed_martial_arts")
        return jsonify([data]), 200
    except:
        return jsonify({"error": "Failed to get default events"}), 500