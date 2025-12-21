from flask import Blueprint, jsonify, current_app, request
import requests
from external_api_client import fetch_odds_data, fetch_events_data
import shared_utils
from shared_utils import constants
from respository import BetRepository
from schemas import SimplifiedOdds, validate_simplified_odds, prepare_for_json

api_bp = Blueprint('api_bp', __name__, url_prefix='/bets')

# class ItemRequest(BaseModel):    

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
    """
    Retrieve odds for a sport with optional region/market filters.
    Query params:
      - sport (required)
      - regions (default: us)
      - markets (default: h2h)
    """
    sport = request.args.get('sport')
    regions = request.args.get('regions', 'us')
    markets = request.args.get('markets', 'h2h')

    if not sport:
        return jsonify({"error": "sport query param is required"}), 400
    if regions not in constants.VALID_REGIONS:
        return jsonify({"error": "Invalid region provided"}), 400
    if markets not in constants.VALID_MARKETS:
        return jsonify({"error": "Invalid markets provided"}), 400

    try:
        data = fetch_odds_data(sport, regions, markets)
        # fetch_odds_data may return a Flask response (e.g., missing API key)
        if hasattr(data, "status_code"):
            return data
        return jsonify(data), 200
    except Exception as e:
        print(f"Error in get_odds: {e}")
        return jsonify({"error": "Failed to get odds data"}), 500

@api_bp.route('/getdefaultodds', methods=['GET'])
def get_default_odds():
    """
    Get default live odds.
    Returns cached odds if available, otherwise fetches and stores new odds.
    Uses schema models for type safety and validation.
    """
    try:
        # Try to initialize repository (may fail if MongoDB not available)
        try:
            repo = BetRepository()
            db_available = True
        except RuntimeError as e:
            print(f"MongoDB not available: {e}")
            db_available = False
            repo = None
        
        # If database is available, try to get cached odds
        if db_available and repo:
            try:
                res = repo.get_live_odds(simplified=True)
                if res:
                    print('returning cached odds')
                    return jsonify(prepare_for_json(res)), 200
            except Exception as e:
                print(f"Error getting cached odds: {e}")
        
        # If no cached odds or DB unavailable, fetch new ones from API
        print('fetching new live odds from external API')
        data = fetch_odds_data(sport='upcoming')
        
        if not data:
            return jsonify({"error": "No odds data available from external API"}), 500
        
        # Try to store in database if available
        if db_available and repo:
            try:
                stored_count = repo.update_live_odds(data)
                print(f"Stored {stored_count} simplified odds")
                # Return from database after storing
                res = repo.get_live_odds(simplified=True)
                if res:
                    return jsonify(prepare_for_json(res)), 200
            except Exception as e:
                print(f"Error storing odds: {e}")
        
        # If database not available or storage failed, return data directly from API
        # Transform using schemas for consistency
        from schemas import simplify_odds_event, simplified_odds_to_dict, prepare_for_json
        simplified_data = []
        for event in data:
            try:
                simplified = simplify_odds_event(event)
                simplified_dict = simplified_odds_to_dict(simplified)
                simplified_data.append(prepare_for_json(simplified_dict))
            except Exception as e:
                print(f"Error transforming odds event: {e}")
                continue
        
        return jsonify(simplified_data), 200
        
    except Exception as e:
        print(f"Error in get_default_odds: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get odds data: {str(e)}"}), 500

@api_bp.route('/getevents', methods=['GET'])
def get_events():
    """
    Retrieve events for a sport.
    Query params:
      - sport (required)
    """
    sport = request.args.get('sport')
    print('getting events for sport: ', sport)
    if not sport:
        data = fetch_events_data("mma_mixed_martial_arts")
        return jsonify(data), 200
    try:
        data = fetch_events_data(sport)
        if hasattr(data, "status_code"):
            return data
        return jsonify(data), 200
    except Exception as e:
        print(f"Error in get_events: {e}")
        return jsonify({"error": "Failed to get events data"}), 500

@api_bp.route('/getdefaultevents', methods=['GET'])
def get_default_events():
    """Gets default events for mma"""
    print('getting default events')
    try:
        data = fetch_events_data("mma_mixed_martial_arts")
        return jsonify([data]), 200
    except:
        return jsonify({"error": "Failed to get default events"}), 500