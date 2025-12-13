from respository import BetRepository
from external_api_client import fetch_sports_data, fetch_odds_data
import threading
import time

def run_on_startup():
    """
    Run startup tasks in background thread to avoid blocking app startup.
    This ensures the server starts quickly for Cloud Run health checks.
    """
    def _startup_tasks():
        try:
            print("[startup] Starting background initialization tasks...")
            time.sleep(2)  # Give app time to fully start
            
            # Check if MongoDB is available before trying to use repository
            from config import db_handle
            if db_handle is None:
                print("[startup] MongoDB not available, skipping database initialization")
                return
            
            try:
                repo = BetRepository()
            except RuntimeError as e:
                print(f'[startup] Cannot initialize repository: {e}')
                return
            
            # Fetch and update sports data
            try:
                sports_data = fetch_sports_data()
                if sports_data:
                    updated_sports = repo.update_sports(sports_data)
                    print(f'[startup] Updated sports: {len(updated_sports.inserted_ids) if updated_sports else 0} sports')
            except Exception as e:
                print(f'[startup] Warning: Could not update sports data: {e}')
            
            # Check if odds data is empty and fetch if needed
            try:
                live_odds = repo.get_live_odds()
                if not live_odds:
                    print('[startup] No live odds found, fetching default odds')
                    default_odds = fetch_odds_data(sport='upcoming')
                    if default_odds:
                        stored_count = repo.update_live_odds(default_odds)
                        print(f'[startup] Stored {stored_count} odds events')
            except Exception as e:
                print(f'[startup] Warning: Could not initialize odds data: {e}')
            
            print("[startup] Background initialization tasks completed")
        except Exception as e:
            print(f'[startup] Error in startup tasks: {e}')
            import traceback
            traceback.print_exc()
            # Don't raise - allow app to continue running
    
    # Run in background thread so it doesn't block app startup
    thread = threading.Thread(target=_startup_tasks, daemon=True)
    thread.start()
    print("[startup] Startup tasks initiated in background")