from config import db_handle
from schemas import (
    simplify_odds_event, 
    odds_event_to_dict, 
    simplified_odds_to_dict,
    dict_to_simplified_odds,
    validate_odds_event,
    validate_simplified_odds,
    prepare_for_json,
    SimplifiedOdds
)

class BetRepository:
    def __init__(self):
        if db_handle is None:
            raise RuntimeError("MongoDB connection not available. Check MONGO_CONNECTION_STRING environment variable.")
        self.sports_collection = db_handle["sports"]
        self.odds_collection = db_handle["live_odds"]
        # Store simplified odds for faster retrieval
        self.simplified_odds_collection = db_handle["simplified_odds"]

    def update_sports(self, sports):
        """Update available sports list"""
        print("updating available sports")
        self.sports_collection.drop()
        res = self.sports_collection.insert_many(sports)
        return res

    def get_live_odds(self, simplified: bool = True) -> list:
        """
        Get live odds from database.
        
        Args:
            simplified: If True, return simplified format. If False, return full format.
        
        Returns:
            List of odds dictionaries (ready for JSON serialization)
        """
        print("getting live odds")
        if simplified:
            results = list(self.simplified_odds_collection.find({}))
            # Use schema utility to prepare for JSON (handles ObjectId, etc.)
            return [prepare_for_json(doc) for doc in results]
        else:
            results = list(self.odds_collection.find({}))
            return [prepare_for_json(doc) for doc in results]
    
    def get_live_odds_as_objects(self):
        """
        Get live odds as SimplifiedOdds objects (for type safety and validation).
        
        Returns:
            List of SimplifiedOdds objects
        """
        results = list(self.simplified_odds_collection.find({}))
        odds_objects = []
        for doc in results:
            try:
                # Convert dict to SimplifiedOdds object
                odds_obj = dict_to_simplified_odds(doc)
                odds_objects.append(odds_obj)
            except Exception as e:
                print(f"Error converting to SimplifiedOdds: {e}")
                continue
        return odds_objects
    
    def update_live_odds(self, odds_data: list):
        """
        Update live odds in database.
        Stores both full format (for reference) and simplified format (for fast retrieval).
        Uses schema validation before storing.
        
        Args:
            odds_data: List of odds events from external API
        
        Returns:
            Number of simplified odds stored
        """
        print("updating live odds")
        
        # Validate and store full format
        self.odds_collection.drop()
        full_odds = []
        for event in odds_data:
            if validate_odds_event(event):
                full_odds.append(odds_event_to_dict(event))
            else:
                print(f"Skipping invalid odds event: {event.get('id', 'unknown')}")
        
        if full_odds:
            self.odds_collection.insert_many(full_odds)
        
        # Transform and store simplified format
        self.simplified_odds_collection.drop()
        simplified_odds = []
        for event in odds_data:
            try:
                # Use schema function to transform
                simplified = simplify_odds_event(event)
                # Convert to dict for MongoDB
                simplified_dict = simplified_odds_to_dict(simplified)
                # Validate before storing
                if validate_simplified_odds(simplified_dict):
                    simplified_odds.append(simplified_dict)
                else:
                    print(f"Skipping invalid simplified odds: {simplified.event_id}")
            except (KeyError, IndexError) as e:
                print(f"Error simplifying odds event {event.get('id', 'unknown')}: {e}")
                continue
        
        if simplified_odds:
            self.simplified_odds_collection.insert_many(simplified_odds)
        
        return len(simplified_odds)