import requests
import os
from flask import current_app, jsonify

def fetch_sports_data():
    """Call external api to retrieve odds"""
    key = current_app.config.get('EXTERNAL_API_KEY')
    if not key:
        return jsonify({"error": "missing api key"}), 500
    
    url = "https://api.the-odds-api.com/v4/sports/"
    params = {
        "apiKey": key
    }
    resp = requests.get(url, params=params, timeout=5)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return jsonify({"error": "external API error", "details": resp.text}), resp.status_code
    print("success - sending sports data")
    return resp.json()

# can't just store this in a single no-sql db
def fetch_odds_data(sport, regions='us', markets='h2h'):
    """Return all odds data"""
    key = current_app.config.get('EXTERNAL_API_KEY')
    if not key:
        return jsonify({"error": "missing api key"}), 500
    
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    params = {
        "apiKey": key,
        "regions": regions,
        "markets": markets
    }
    resp = requests.get(url, params=params, timeout=7)
    try:
        resp.raise_for_status
    except requests.HTTPError:
        return jsonify({"error": "external API error", "details": resp.text}), resp.status_code
    print("success - sending odds data")
    # WILL NEED TO DETERMINE IF NEED TO UPDATE ANY DB
    return resp.json()

def fetch_events_data(sport):
    """Return all events data"""
    key = current_app.config.get('EXTERNAL_API_KEY')
    if not key:
        return jsonify({"error": "missing api key"}), 500
    
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/events"
    params = {
        "apiKey": key
    }
    resp = requests.get(url, params=params, timeout=7)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return jsonify({"error": "external API error", "details": resp.text}), resp.status_code
    print("success - sending events data")
    return resp.json()