from flask import Flask, jsonify
from flask.cli import load_dotenv
from routes.api_routes import api_bp
import os
import config
from startup_tasks import run_on_startup

load_dotenv()

app = Flask(__name__)
app.config['EXTERNAL_API_KEY'] = os.getenv('ODDS_API_KEY')
app.register_blueprint(api_bp)

# Run startup tasks in background (non-blocking)
# This ensures the app starts quickly for Cloud Run health checks
try:
    run_on_startup()
except Exception as e:
    print(f"Warning: Startup tasks failed, but continuing: {e}")
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
