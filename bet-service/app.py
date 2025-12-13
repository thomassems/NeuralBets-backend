import sys
import traceback

# Load environment variables first
try:
    from flask.cli import load_dotenv
    load_dotenv()
    print("[app] Environment variables loaded")
except Exception as e:
    print(f"[app] Warning: Could not load .env file: {e}")

from flask import Flask, jsonify
import os

# Create Flask app FIRST - this must succeed
app = Flask(__name__)
print("[app] Flask app created")

# Set basic config
app.config['EXTERNAL_API_KEY'] = os.getenv('ODDS_API_KEY')
print("[app] Config set")

# Import config early to initialize MongoDB connection (if available)
try:
    import config
    print("[app] Config module loaded successfully")
except Exception as e:
    print(f"[app] Warning: Error loading config: {e}")
    traceback.print_exc()
    # Continue anyway - app can run without MongoDB

# Import routes with error handling
try:
    print("[app] Attempting to import routes.api_routes...")
    from routes.api_routes import api_bp
    print("[app] API routes imported successfully")
    
    print("[app] Attempting to register blueprint...")
    app.register_blueprint(api_bp)
    print("[app] Blueprint registered successfully")
except ImportError as e:
    print(f"[app] CRITICAL ERROR: Import failed: {e}")
    traceback.print_exc()
    sys.exit(1)  # Can't run without routes
except Exception as e:
    print(f"[app] CRITICAL ERROR: Failed to register routes: {e}")
    traceback.print_exc()
    sys.exit(1)  # Can't run without routes

# Import and run startup tasks
try:
    from startup_tasks import run_on_startup
    print("[app] Startup tasks module loaded")
    run_on_startup()
    print("[app] Startup tasks initiated")
except Exception as e:
    print(f"[app] Warning: Startup tasks failed: {e}")
    traceback.print_exc()
    # Don't fail app startup if startup tasks fail

@app.route('/', methods=['GET'])
def home():
    """Returns a simple greeting message from the API."""
    return jsonify({
        "message": "Welcome to the Dockerized Flask Backend!",
        "status": "Running successfully",
        "service": "Flask API"
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint for container health checks."""
    return jsonify({"status": "ok"}), 200
