"""
Repository layer for wallet operations.
Handles all database interactions for wallets and transactions.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import asdict
import uuid
from wallet_schemas import (
    Wallet, Transaction, wallet_to_dict, dict_to_wallet,
    transaction_to_dict, dict_to_transaction, create_new_wallet, CHALLENGE_CONFIGS
)


# In-memory storage for development (replace with actual database in production)
# This simulates Firebase Firestore or MongoDB
wallets_db: Dict[str, Dict[str, Any]] = {}
transactions_db: Dict[str, Dict[str, Any]] = {}


def get_wallet_by_user_id(user_id: str) -> Optional[Wallet]:
    """
    Retrieve wallet for a specific user.
    
    Args:
        user_id: Firebase user ID
    
    Returns:
        Wallet object if found, None otherwise
    """
    wallet_data = wallets_db.get(user_id)
    if wallet_data:
        return dict_to_wallet(wallet_data)
    return None


def create_wallet(user_id: str, challenge_type: str, custom_balance: Optional[float] = None) -> Wallet:
    """
    Create a new wallet for a user.
    
    Args:
        user_id: Firebase user ID
        challenge_type: Type of challenge
        custom_balance: Custom starting balance for FREE_PLAY mode
    
    Returns:
        Created Wallet object
    """
    # Check if wallet already exists
    existing_wallet = get_wallet_by_user_id(user_id)
    if existing_wallet:
        raise ValueError("Wallet already exists for this user")
    
    wallet = create_new_wallet(user_id, challenge_type, custom_balance)
    wallets_db[user_id] = wallet_to_dict(wallet)
    
    # Create initial transaction
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        type='challenge_start',
        amount=wallet.starting_balance,
        balance_before=0.0,
        balance_after=wallet.starting_balance,
        bet_id=None,
        description=f"Started {CHALLENGE_CONFIGS[challenge_type].display_name}",
        created_at=datetime.utcnow().isoformat()
    )
    transactions_db[transaction_id] = transaction_to_dict(transaction)
    
    return wallet


def update_wallet_balance(user_id: str, new_balance: float) -> Wallet:
    """
    Update wallet balance.
    
    Args:
        user_id: Firebase user ID
        new_balance: New balance amount
    
    Returns:
        Updated Wallet object
    """
    wallet_data = wallets_db.get(user_id)
    if not wallet_data:
        raise ValueError("Wallet not found")
    
    wallet_data['balance'] = new_balance
    wallet_data['updated_at'] = datetime.utcnow().isoformat()
    wallets_db[user_id] = wallet_data
    
    return dict_to_wallet(wallet_data)


def record_bet_placed(user_id: str, bet_amount: float, bet_id: str) -> Wallet:
    """
    Record a bet placement and deduct from balance.
    
    Args:
        user_id: Firebase user ID
        bet_amount: Amount wagered
        bet_id: Unique bet identifier
    
    Returns:
        Updated Wallet object
    """
    wallet_data = wallets_db.get(user_id)
    if not wallet_data:
        raise ValueError("Wallet not found")
    
    wallet = dict_to_wallet(wallet_data)
    
    if wallet.balance < bet_amount:
        raise ValueError("Insufficient balance")
    
    # Update wallet
    balance_before = wallet.balance
    wallet.balance -= bet_amount
    wallet.total_wagered += bet_amount
    wallet.bets_placed += 1
    wallet.updated_at = datetime.utcnow().isoformat()
    
    wallets_db[user_id] = wallet_to_dict(wallet)
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        type='bet_placed',
        amount=-bet_amount,
        balance_before=balance_before,
        balance_after=wallet.balance,
        bet_id=bet_id,
        description=f"Placed bet of ${bet_amount:.2f}",
        created_at=datetime.utcnow().isoformat()
    )
    transactions_db[transaction_id] = transaction_to_dict(transaction)
    
    return wallet


def record_bet_won(user_id: str, payout: float, bet_id: str) -> Wallet:
    """
    Record a winning bet and add payout to balance.
    
    Args:
        user_id: Firebase user ID
        payout: Amount won (including original stake)
        bet_id: Unique bet identifier
    
    Returns:
        Updated Wallet object
    """
    wallet_data = wallets_db.get(user_id)
    if not wallet_data:
        raise ValueError("Wallet not found")
    
    wallet = dict_to_wallet(wallet_data)
    
    balance_before = wallet.balance
    wallet.balance += payout
    wallet.total_won += payout
    wallet.bets_won += 1
    wallet.updated_at = datetime.utcnow().isoformat()
    
    wallets_db[user_id] = wallet_to_dict(wallet)
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        type='bet_won',
        amount=payout,
        balance_before=balance_before,
        balance_after=wallet.balance,
        bet_id=bet_id,
        description=f"Bet won: +${payout:.2f}",
        created_at=datetime.utcnow().isoformat()
    )
    transactions_db[transaction_id] = transaction_to_dict(transaction)
    
    return wallet


def record_bet_lost(user_id: str, amount_lost: float, bet_id: str) -> Wallet:
    """
    Record a losing bet (balance already deducted on placement).
    
    Args:
        user_id: Firebase user ID
        amount_lost: Amount that was wagered and lost
        bet_id: Unique bet identifier
    
    Returns:
        Updated Wallet object
    """
    wallet_data = wallets_db.get(user_id)
    if not wallet_data:
        raise ValueError("Wallet not found")
    
    wallet = dict_to_wallet(wallet_data)
    
    wallet.total_lost += amount_lost
    wallet.bets_lost += 1
    wallet.updated_at = datetime.utcnow().isoformat()
    
    wallets_db[user_id] = wallet_to_dict(wallet)
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        type='bet_lost',
        amount=0.0,
        balance_before=wallet.balance,
        balance_after=wallet.balance,
        bet_id=bet_id,
        description=f"Bet lost: -${amount_lost:.2f}",
        created_at=datetime.utcnow().isoformat()
    )
    transactions_db[transaction_id] = transaction_to_dict(transaction)
    
    return wallet


def get_transactions_by_user_id(user_id: str, limit: int = 50) -> List[Transaction]:
    """
    Get transaction history for a user.
    
    Args:
        user_id: Firebase user ID
        limit: Maximum number of transactions to return
    
    Returns:
        List of Transaction objects
    """
    user_transactions = [
        dict_to_transaction(t) for t in transactions_db.values()
        if t['user_id'] == user_id
    ]
    
    # Sort by created_at descending (most recent first)
    user_transactions.sort(key=lambda t: t.created_at, reverse=True)
    
    return user_transactions[:limit]


def reset_wallet(user_id: str) -> Wallet:
    """
    Reset a wallet to its starting balance and clear stats.
    
    Args:
        user_id: Firebase user ID
    
    Returns:
        Reset Wallet object
    """
    wallet_data = wallets_db.get(user_id)
    if not wallet_data:
        raise ValueError("Wallet not found")
    
    wallet = dict_to_wallet(wallet_data)
    
    # Reset to starting balance
    balance_before = wallet.balance
    wallet.balance = wallet.starting_balance
    wallet.total_wagered = 0.0
    wallet.total_won = 0.0
    wallet.total_lost = 0.0
    wallet.bets_placed = 0
    wallet.bets_won = 0
    wallet.bets_lost = 0
    wallet.updated_at = datetime.utcnow().isoformat()
    
    wallets_db[user_id] = wallet_to_dict(wallet)
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        type='balance_adjustment',
        amount=wallet.starting_balance - balance_before,
        balance_before=balance_before,
        balance_after=wallet.balance,
        bet_id=None,
        description="Wallet reset to starting balance",
        created_at=datetime.utcnow().isoformat()
    )
    transactions_db[transaction_id] = transaction_to_dict(transaction)
    
    return wallet


