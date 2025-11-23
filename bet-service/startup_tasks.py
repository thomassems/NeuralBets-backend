from respository import BetRepository
from external_api_client import fetch_sports_data

def run_on_startup():
    repo = BetRepository()
    sports_data = fetch_sports_data()
    updated_sports = repo.update_sports(sports_data)
    print('updated sports: ', updated_sports)
    # if odds data is empty, need to fill it
    live_odds = repo.get_live_odds()
    if not live_odds:
        print('no live odds found, fetching default odds')
        default_odds = fetch_odds_data(sport='upcoming')
        repo.update_live_odds(default_odds)