from config import db_handle

class BetRepository:
    def __init__(self):
        self.sports_collection = db_handle["sports"]
        self.odds_collection = db_handle["default_odds"]

    def update_sports(self, sports):
        print("updating available sports")
        self.sports_collection.drop()
        res = self.sports_collection.insert_many(sports)
        return res

    def get_default_odds(self):
        print("getting default odds")
        return list(self.odds_collection.find({}))