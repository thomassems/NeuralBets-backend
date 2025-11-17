from flask import Flask, jsonify
from flask.cli import load_dotenv
from routes.api_routes import api_bp

load_dotenv()

app = Flask(__name__)

app.register_blueprint(api_bp)

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
