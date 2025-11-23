from config import db_handle

class BetRepository:
    def __init__(self):
        self.sports_collection = db_handle["sports"]
        self.odds_collection = db_handle["live_odds"]

    def update_sports(self, sports):
        print("updating available sports")
        self.sports_collection.drop()
        res = self.sports_collection.insert_many(sports)
        return res

    def get_live_odds(self):
        print("getting live odds")
        # will have to be changed to update/drop the odds every so often
        results = list(self.odds_collection.find({}))
        for doc in results:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        return results
    
    def update_live_odds(self, odds):
        print("updating live odds")
        self.odds_collection.drop()
        res = self.odds_collection.insert_many(odds)
        return res