from config import db_handle

class BetRepository:
    def __init__(self):
        self.collection = db_handle["sports"]

    def update_sports(self, sports):
        print("updating available sports")
        self.collection.drop()
        res = self.collection.insert_many(sports)