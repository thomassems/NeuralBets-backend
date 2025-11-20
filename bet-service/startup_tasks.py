from respository import BetRepository
from external_api_client import fetch_sports_data

def run_on_startup():
    repo = BetRepository()
    sports_data = fetch_sports_data()
    repo.update_sports(sports_data)
    # if odds data is empty, need to fill it