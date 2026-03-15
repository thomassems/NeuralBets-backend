from flask import Blueprint, jsonify, request
from wallet_repository import (
    get_wallet_by_user_id, create_wallet, update_wallet_balance,
    record_bet_placed, record_bet_won, record_bet_lost,
    get_transactions_by_user_id, reset_wallet
)
from wallet_schemas import wallet_to_dict, transaction_to_dict, get_all_challenge_configs

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

@api_bp.route('/status', methods=['GET'])
def api_status():
    """Returns the status of the sub-API service."""
    return jsonify({
        "status": "online",
        "version": "1.0",
        "service_area": "Modular API Blueprint"
    }), 200

@api_bp.route('/users', methods=['GET'])
def list_users():
    """Placeholder endpoint for managing user resources."""
    # In a real application, this would query the database
    return jsonify([
        {"id": 1, "username": "jane_doe"},
        {"id": 2, "username": "john_smith"}
    ]), 200


# ============================================================================
# WALLET ENDPOINTS
# ============================================================================

@api_bp.route('/wallet/<user_id>', methods=['GET'])
def get_wallet(user_id: str):
    """Get wallet for a specific user."""
    try:
        wallet = get_wallet_by_user_id(user_id)
        if wallet:
            return jsonify(wallet_to_dict(wallet)), 200
        else:
            return jsonify({"error": "Wallet not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/wallet', methods=['POST'])
def create_user_wallet():
    """Create a new wallet for a user."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        challenge_type = data.get('challenge_type')
        custom_balance = data.get('custom_balance')
        
        if not user_id or not challenge_type:
            return jsonify({"error": "user_id and challenge_type are required"}), 400
        
        wallet = create_wallet(user_id, challenge_type, custom_balance)
        return jsonify(wallet_to_dict(wallet)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/wallet/<user_id>/bet', methods=['POST'])
def place_bet(user_id: str):
    """Record a bet placement and deduct from balance."""
    try:
        data = request.get_json()
        bet_amount = data.get('bet_amount')
        bet_id = data.get('bet_id')
        
        if not bet_amount or not bet_id:
            return jsonify({"error": "bet_amount and bet_id are required"}), 400
        
        wallet = record_bet_placed(user_id, float(bet_amount), bet_id)
        return jsonify(wallet_to_dict(wallet)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/wallet/<user_id>/win', methods=['POST'])
def win_bet(user_id: str):
    """Record a winning bet and add payout to balance."""
    try:
        data = request.get_json()
        payout = data.get('payout')
        bet_id = data.get('bet_id')
        
        if not payout or not bet_id:
            return jsonify({"error": "payout and bet_id are required"}), 400
        
        wallet = record_bet_won(user_id, float(payout), bet_id)
        return jsonify(wallet_to_dict(wallet)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/wallet/<user_id>/lose', methods=['POST'])
def lose_bet(user_id: str):
    """Record a losing bet."""
    try:
        data = request.get_json()
        amount_lost = data.get('amount_lost')
        bet_id = data.get('bet_id')
        
        if not amount_lost or not bet_id:
            return jsonify({"error": "amount_lost and bet_id are required"}), 400
        
        wallet = record_bet_lost(user_id, float(amount_lost), bet_id)
        return jsonify(wallet_to_dict(wallet)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/wallet/<user_id>/transactions', methods=['GET'])
def get_transactions(user_id: str):
    """Get transaction history for a user."""
    try:
        limit = request.args.get('limit', 50, type=int)
        transactions = get_transactions_by_user_id(user_id, limit)
        return jsonify([transaction_to_dict(t) for t in transactions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/wallet/<user_id>/reset', methods=['POST'])
def reset_user_wallet(user_id: str):
    """Reset wallet to starting balance."""
    try:
        wallet = reset_wallet(user_id)
        return jsonify(wallet_to_dict(wallet)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/challenges', methods=['GET'])
def get_challenges():
    """Get all available challenge configurations."""
    try:
        configs = get_all_challenge_configs()
        return jsonify(configs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500