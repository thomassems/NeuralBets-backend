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
from flask_cors import CORS
import os

# Create Flask app FIRST - this must succeed
app = Flask(__name__)
print("[app] Flask app created")

# Configure CORS before registering blueprints
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3001,https://neuralbets.vercel.app")
allowed_origins = [o.strip() for o in cors_origins.split(",") if o.strip()]
CORS(app, resources={r"/bets/*": {"origins": allowed_origins}, r"/health": {"origins": allowed_origins}, r"/": {"origins": allowed_origins}})
print(f"[app] CORS enabled for origins: {allowed_origins}")

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
routes_loaded = False
try:
    print("[app] Attempting to import routes.api_routes...")
    from routes.api_routes import api_bp
    print("[app] API routes imported successfully")
    
    print("[app] Attempting to register blueprint...")
    app.register_blueprint(api_bp)
    print("[app] Blueprint registered successfully")
    routes_loaded = True
except Exception as e:
    print(f"[app] CRITICAL ERROR: Failed to load routes: {e}")
    traceback.print_exc()
    # Create error route so app can at least start and show the error
    @app.route('/error')
    def import_error():
        return jsonify({
            "error": "Routes failed to load", 
            "details": str(e),
            "message": "Check logs for full traceback"
        }), 500
    # Don't raise - allow app to start so we can debug
    print("[app] App will start with limited functionality due to route import failure")

# Import and run startup tasks
try:
    from startup_tasks import run_on_startup
    print("[app] Startup tasks module loaded")
    run_on_startup(app)
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
