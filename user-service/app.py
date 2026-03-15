from flask import Flask, jsonify
from flask.cli import load_dotenv
from flask_cors import CORS
from routes.api_routes import api_bp

load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:3001", "https://neuralbets.vercel.app"]},
    r"/health": {"origins": "*"}
})

app.register_blueprint(api_bp)

@app.route('/', methods=['GET'])
def home():
    """Returns a simple greeting message from the API."""
    return jsonify({
        "message": "Welcome to the User Service!",
        "status": "Running successfully",
        "service": "User & Wallet API"
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint for container health checks."""
    return jsonify({"status": "ok"}), 200
