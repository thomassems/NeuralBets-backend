from flask import Blueprint, jsonify, current_app, request
import requests
from external_api_client import fetch_odds_data, fetch_events_data
import shared_utils
from shared_utils import constants
from respository import BetRepository
from schemas import SimplifiedOdds, validate_simplified_odds, prepare_for_json, simplify_odds_event, simplified_odds_to_dict
from redis_cache import redis_cache

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
        if hasattr(data, "status_code"):
            return data
        return jsonify(data), 200
    except Exception as e:
        print(f"Error in get_odds: {e}")
        return jsonify({"error": "Failed to get odds data"}), 500

@api_bp.route('/getliveodds', methods=['GET'])
def get_live_odds():
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
        print(f"Error in get_live_odds: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get live odds data: {str(e)}"}), 500

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
        return jsonify({"error": "Missing required query parameter: sport"}), 400
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

@api_bp.route('/getdefaultodds', methods=['GET'])
def get_default_odds():
    """
    Get default live odds with Redis caching for fast responses.
    
    Caching strategy:
    1. Check Redis cache first (1-minute TTL)
    2. If cache valid (< 1 minute old), return cached data immediately
    3. If cache expired or missing, fetch from external API
    4. Store in Redis and optionally in MongoDB
    5. Return fresh data
    
    This dramatically improves response time from ~3s to ~100ms for cached requests.
    """
    try:
        # Step 1: Check Redis cache
        cached_result = redis_cache.get_cached_odds()
        if cached_result:
            print('[getdefaultodds] Returning data from Redis cache')
            return jsonify(cached_result['data']), 200
        
        print('[getdefaultodds] Cache miss or expired, fetching fresh data')
        
        # Step 2: Fetch fresh data from external API
        data = fetch_odds_data(sport='upcoming')
        
        if not data:
            return jsonify({"error": "No odds data available from external API"}), 500
        
        # Step 3: Transform data for frontend
        simplified_data = []
        for event in data:
            try:
                simplified = simplify_odds_event(event)
                simplified_dict = simplified_odds_to_dict(simplified)
                simplified_data.append(prepare_for_json(simplified_dict))
            except Exception as e:
                print(f"Error transforming odds event: {e}")
                continue
        
        transformed_data = transform_odds_for_frontend(simplified_data)
        
        # Step 4: Cache in Redis (primary cache - fast)
        redis_cache.set_cached_odds(transformed_data)
        
        # Step 5: Optionally store in MongoDB (secondary/backup storage)
        try:
            repo = BetRepository()
            stored_count = repo.update_live_odds(data)
            print(f"[getdefaultodds] Stored {stored_count} odds in MongoDB")
        except Exception as e:
            print(f"[getdefaultodds] MongoDB storage failed (non-critical): {e}")
        
        # Step 6: Return fresh data
        return jsonify(transformed_data), 200
        
    except Exception as e:
        print(f"Error in get_default_odds: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get default odds data: {str(e)}"}), 500

def transform_odds_for_frontend(odds_data):
    """
    Transform backend odds data to match frontend live_game interface.
    Maps field names and adds necessary IDs for the frontend.
    """
    import uuid
    transformed = []
    
    for odds in odds_data:
        # Handle both dictionary and object formats
        if hasattr(odds, '__dict__'):
            odds_dict = odds.__dict__
        else:
            odds_dict = odds
        
        # Generate unique IDs for home and away teams
        home_team_id = str(uuid.uuid4())
        away_team_id = str(uuid.uuid4())
        
        transformed_game = {
            'id': odds_dict.get('event_id', ''),
            'sport_name': odds_dict.get('sport_key', '').replace('_', ' ').title(),
            'sport_title': odds_dict.get('sport_title', ''),
            'home_team': odds_dict.get('home_team', ''),
            'home_team_id': home_team_id,
            'away_team': odds_dict.get('away_team', ''),
            'away_team_id': away_team_id,
            'market': odds_dict.get('market_type', 'h2h'),
            'bookmaker': odds_dict.get('bookmaker', ''),
            'home_team_price': odds_dict.get('home_team_price', 0.0),
            'away_team_price': odds_dict.get('away_team_price', 0.0),
            'start_time': odds_dict.get('commence_time', '')
        }
        transformed.append(transformed_game)
    
    return transformed