"""
Data schema and models for the bet service.
Defines the structure of data used throughout the service.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime


# ============================================================================
# CORE DATA MODELS
# ============================================================================

@dataclass
class Outcome:
    """Represents a betting outcome (team/player and their odds)"""
    name: str
    price: float


@dataclass
class Market:
    """Represents a betting market (e.g., h2h, spreads, totals)"""
    key: str
    last_update: str
    outcomes: List[Outcome]


@dataclass
class Bookmaker:
    """Represents a bookmaker with their markets"""
    key: str
    title: str
    last_update: str
    markets: List[Market]


@dataclass
class OddsEvent:
    """Full odds event with all bookmakers - matches external API format"""
    id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str
    bookmakers: List[Bookmaker]


@dataclass
class SimplifiedOdds:
    """Simplified odds format optimized for API responses"""
    event_id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str
    market_type: str
    home_team_price: float
    away_team_price: float
    bookmaker: str
    last_update: str


# ============================================================================
# TRANSFORMATION FUNCTIONS
# ============================================================================

def simplify_odds_event(event: Dict[str, Any], bookmaker_index: int = 0, market_index: int = 0) -> SimplifiedOdds:
    """
    Transform a full odds event into a simplified format.
    
    Args:
        event: Full odds event dictionary from API
        bookmaker_index: Which bookmaker to use (default: first one)
        market_index: Which market to use (default: first one)
    
    Returns:
        SimplifiedOdds object
    """
    bookmaker = event['bookmakers'][bookmaker_index] if event.get('bookmakers') else {}
    market = bookmaker.get('markets', [{}])[market_index] if bookmaker.get('markets') else {}
    outcomes = market.get('outcomes', [])
    
    # Extract home and away team prices
    home_price = None
    away_price = None
    
    for outcome in outcomes:
        if outcome.get('name') == event.get('home_team'):
            home_price = outcome.get('price')
        elif outcome.get('name') == event.get('away_team'):
            away_price = outcome.get('price')
    
    # If prices not found by name, use first two outcomes
    if home_price is None and len(outcomes) >= 2:
        home_price = outcomes[0].get('price')
        away_price = outcomes[1].get('price')
    
# return SimplifiedOdds(
#         event_id=event.get('id', ''),
#         sport_key=event.get('sport_key', ''),
#         sport_name=event.get('sport_name', ''),
#         sport_title=event.get('sport_title', ''),
#         start_time=event.get('commence_time', ''),
#         home_team=event.get('home_team', ''),
#         away_team=event.get('away_team', ''),
#         market=market.get('key', ''),
#         bookmaker=bookmaker.get('key', ''),
#         home_team_id=event.get('home_team_id', ''),
#         away_team_id=event.get('away_team_id', ''),
#         home_team_price=home_price or 0.0,
#         away_team_price=away_price or 0.0,
#         last_update=market.get('last_update', '')
#     )

    return SimplifiedOdds(
        event_id=event.get('id', ''),
        sport_key=event.get('sport_key', ''),
        sport_title=event.get('sport_title', ''),
        commence_time=event.get('commence_time', ''),
        home_team=event.get('home_team', ''),
        away_team=event.get('away_team', ''),
        market_type=market.get('key', ''),
        home_team_price=home_price or 0.0,
        away_team_price=away_price or 0.0,
        bookmaker=bookmaker.get('title', ''),
        last_update=market.get('last_update', '')
    )


def odds_event_to_dict(event: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an odds event to a dictionary suitable for MongoDB storage"""
    # Remove _id if present (will be added by MongoDB)
    event_dict = {k: v for k, v in event.items() if k != '_id'}
    return event_dict


def simplified_odds_to_dict(odds: SimplifiedOdds) -> Dict[str, Any]:
    """Convert SimplifiedOdds to dictionary for JSON serialization"""
    return asdict(odds)


def dict_to_simplified_odds(data: Dict[str, Any]) -> SimplifiedOdds:
    """Convert dictionary (from MongoDB) to SimplifiedOdds object"""
    return SimplifiedOdds(**data)


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_odds_event(event: Dict[str, Any]) -> bool:
    """
    Validate that an odds event has all required fields.
    
    Args:
        event: Dictionary containing odds event data
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['id', 'sport_key', 'home_team', 'away_team', 'commence_time']
    return all(field in event for field in required_fields)


def validate_simplified_odds(odds: Dict[str, Any]) -> bool:
    """
    Validate that simplified odds have all required fields.
    
    Args:
        odds: Dictionary containing simplified odds data
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['event_id', 'sport_key', 'home_team', 'away_team', 
                       'home_team_price', 'away_team_price']
    return all(field in odds for field in required_fields)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def convert_objectid_to_string(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB ObjectId to string for JSON serialization.
    
    Args:
        doc: MongoDB document
    
    Returns:
        Document with _id converted to string
    """
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc


def prepare_for_json(data: Any) -> Any:
    """
    Recursively prepare data structure for JSON serialization.
    Handles ObjectId, datetime, and other non-serializable types.
    
    Args:
        data: Data structure to prepare
    
    Returns:
        JSON-serializable data structure
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key == '_id':
                result[key] = str(value)
            else:
                result[key] = prepare_for_json(value)
        return result
    elif isinstance(data, list):
        return [prepare_for_json(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data
