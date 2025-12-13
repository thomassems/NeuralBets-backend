"""
Examples of how to use the data models from schemas.py
This file demonstrates various use cases - you can reference this for patterns.
"""

from schemas import (
    SimplifiedOdds,
    OddsEvent,
    simplify_odds_event,
    simplified_odds_to_dict,
    dict_to_simplified_odds,
    validate_odds_event,
    validate_simplified_odds,
    prepare_for_json
)


# ============================================================================
# EXAMPLE 1: Creating a SimplifiedOdds object directly
# ============================================================================

def example_create_odds_object():
    """Create a SimplifiedOdds object with known data"""
    odds = SimplifiedOdds(
        event_id="abc123",
        sport_key="americanfootball_nfl",
        sport_title="NFL",
        commence_time="2025-11-23T21:00:00Z",
        home_team="Dallas Cowboys",
        away_team="Philadelphia Eagles",
        market_type="h2h",
        home_team_price=2.36,
        away_team_price=1.62,
        bookmaker="DraftKings",
        last_update="2025-11-23T21:19:48Z"
    )
    
    # Convert to dictionary for storage or JSON
    odds_dict = simplified_odds_to_dict(odds)
    print("Odds as dict:", odds_dict)
    
    # Access properties directly
    print(f"Home team: {odds.home_team}")
    print(f"Home price: {odds.home_team_price}")


# ============================================================================
# EXAMPLE 2: Transforming external API data
# ============================================================================

def example_transform_api_data():
    """Transform data from external API into simplified format"""
    # This is what you get from the external API
    api_response = {
        "id": "abc123",
        "sport_key": "americanfootball_nfl",
        "sport_title": "NFL",
        "commence_time": "2025-11-23T21:00:00Z",
        "home_team": "Dallas Cowboys",
        "away_team": "Philadelphia Eagles",
        "bookmakers": [
            {
                "key": "draftkings",
                "title": "DraftKings",
                "last_update": "2025-11-23T21:19:48Z",
                "markets": [
                    {
                        "key": "h2h",
                        "last_update": "2025-11-23T21:19:48Z",
                        "outcomes": [
                            {"name": "Dallas Cowboys", "price": 2.36},
                            {"name": "Philadelphia Eagles", "price": 1.62}
                        ]
                    }
                ]
            }
        ]
    }
    
    # Validate first
    if validate_odds_event(api_response):
        # Transform using schema function
        simplified = simplify_odds_event(api_response)
        print(f"Transformed: {simplified.home_team} vs {simplified.away_team}")
        print(f"Prices: {simplified.home_team_price} / {simplified.away_team_price}")
        
        # Convert to dict for storage
        simplified_dict = simplified_odds_to_dict(simplified)
        return simplified_dict
    else:
        print("Invalid odds event")
        return None


# ============================================================================
# EXAMPLE 3: Working with data from MongoDB
# ============================================================================

def example_work_with_mongodb_data():
    """Convert MongoDB document back to object"""
    # This is what you get from MongoDB
    mongo_doc = {
        "_id": "507f1f77bcf86cd799439011",  # ObjectId as string
        "event_id": "abc123",
        "sport_key": "americanfootball_nfl",
        "home_team": "Dallas Cowboys",
        "away_team": "Philadelphia Eagles",
        "home_team_price": 2.36,
        "away_team_price": 1.62,
        # ... other fields
    }
    
    # Convert to object for type-safe access
    odds_obj = dict_to_simplified_odds(mongo_doc)
    
    # Now you can use it as an object
    if odds_obj.home_team_price > 2.0:
        print(f"{odds_obj.home_team} is an underdog")
    
    # Or convert back to dict for JSON response
    response_dict = simplified_odds_to_dict(odds_obj)
    return response_dict


# ============================================================================
# EXAMPLE 4: Validating data before processing
# ============================================================================

def example_validate_data():
    """Validate data before storing or processing"""
    data = {
        "event_id": "abc123",
        "sport_key": "nfl",
        "home_team": "Dallas",
        "away_team": "Philadelphia",
        "home_team_price": 2.36,
        "away_team_price": 1.62
    }
    
    if validate_simplified_odds(data):
        print("Data is valid, can proceed")
        # Store in database, process, etc.
    else:
        print("Data is invalid, skipping")


# ============================================================================
# EXAMPLE 5: Preparing data for JSON response
# ============================================================================

def example_prepare_for_json():
    """Ensure data is JSON-serializable"""
    data = {
        "_id": "507f1f77bcf86cd799439011",  # This might be ObjectId
        "event_id": "abc123",
        "prices": [1.5, 2.3, 3.1],
        "metadata": {
            "created_at": "2025-11-23T21:00:00Z",
            "nested": {
                "value": 123
            }
        }
    }
    
    # prepare_for_json handles ObjectId, datetime, nested structures
    json_ready = prepare_for_json(data)
    # Now safe to use with jsonify()
    return json_ready


# ============================================================================
# EXAMPLE 6: Using models in business logic
# ============================================================================

def example_business_logic():
    """Use models for calculations and business logic"""
    odds1 = SimplifiedOdds(
        event_id="event1",
        sport_key="nfl",
        sport_title="NFL",
        commence_time="2025-11-23T21:00:00Z",
        home_team="Team A",
        away_team="Team B",
        market_type="h2h",
        home_team_price=2.0,
        away_team_price=1.8,
        bookmaker="DraftKings",
        last_update="2025-11-23T21:00:00Z"
    )
    
    odds2 = SimplifiedOdds(
        event_id="event2",
        sport_key="nfl",
        sport_title="NFL",
        commence_time="2025-11-23T21:00:00Z",
        home_team="Team C",
        away_team="Team D",
        market_type="h2h",
        home_team_price=1.5,
        away_team_price=2.5,
        bookmaker="FanDuel",
        last_update="2025-11-23T21:00:00Z"
    )
    
    # Compare odds
    if odds1.home_team_price < odds2.home_team_price:
        print(f"{odds1.home_team} has better odds than {odds2.home_team}")
    
    # Calculate implied probability
    home_prob = 1 / odds1.home_team_price
    away_prob = 1 / odds1.away_team_price
    print(f"Implied probabilities: {home_prob:.2%} / {away_prob:.2%}")


# ============================================================================
# EXAMPLE 7: Filtering and querying with models
# ============================================================================

def example_filter_odds(odds_list: list[SimplifiedOdds], sport: str):
    """Filter odds by sport using model properties"""
    filtered = [odds for odds in odds_list if odds.sport_key == sport]
    return filtered


def example_find_best_odds(odds_list: list[SimplifiedOdds]):
    """Find the best (highest) odds for home team"""
    if not odds_list:
        return None
    
    best_odds = max(odds_list, key=lambda x: x.home_team_price)
    return best_odds





