from flask import Flask, jsonify
from flask.cli import load_dotenv

load_dotenv()


app = Flask(__name__)

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

if __name__ == '__main__':
    # Default local run configuration
    app.run(host='0.0.0.0', port=5001, debug=True)