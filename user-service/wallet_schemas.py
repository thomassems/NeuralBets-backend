"""
Wallet and challenge schemas for user balance management.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ChallengeType(str, Enum):
    """Types of betting challenges available"""
    CHALLENGE_100_1000 = "challenge_100_1000"
    CHALLENGE_500_5000 = "challenge_500_5000"
    CHALLENGE_1000_10000 = "challenge_1000_10000"
    FREE_PLAY = "free_play"


@dataclass
class ChallengeConfig:
    """Configuration for a specific challenge type"""
    challenge_type: str
    starting_balance: float
    target_balance: float
    min_balance: float
    max_balance: float
    display_name: str
    description: str


# Challenge configurations
CHALLENGE_CONFIGS = {
    ChallengeType.CHALLENGE_100_1000: ChallengeConfig(
        challenge_type=ChallengeType.CHALLENGE_100_1000,
        starting_balance=100.0,
        target_balance=1000.0,
        min_balance=0.0,
        max_balance=1000.0,
        display_name="$100 to $1,000 Challenge",
        description="Start with $100 and reach $1,000"
    ),
    ChallengeType.CHALLENGE_500_5000: ChallengeConfig(
        challenge_type=ChallengeType.CHALLENGE_500_5000,
        starting_balance=500.0,
        target_balance=5000.0,
        min_balance=0.0,
        max_balance=5000.0,
        display_name="$500 to $5,000 Challenge",
        description="Start with $500 and reach $5,000"
    ),
    ChallengeType.CHALLENGE_1000_10000: ChallengeConfig(
        challenge_type=ChallengeType.CHALLENGE_1000_10000,
        starting_balance=1000.0,
        target_balance=10000.0,
        min_balance=0.0,
        max_balance=10000.0,
        display_name="$1,000 to $10,000 Challenge",
        description="Start with $1,000 and reach $10,000"
    ),
    ChallengeType.FREE_PLAY: ChallengeConfig(
        challenge_type=ChallengeType.FREE_PLAY,
        starting_balance=0.0,
        target_balance=0.0,
        min_balance=0.0,
        max_balance=1000000.0,
        display_name="Free Play",
        description="Choose your own starting balance"
    )
}


@dataclass
class Wallet:
    """User wallet data for simulated betting"""
    user_id: str
    balance: float
    challenge_type: str
    starting_balance: float
    target_balance: Optional[float]
    created_at: str
    updated_at: str
    total_wagered: float = 0.0
    total_won: float = 0.0
    total_lost: float = 0.0
    bets_placed: int = 0
    bets_won: int = 0
    bets_lost: int = 0


@dataclass
class Transaction:
    """Record of a wallet transaction"""
    transaction_id: str
    user_id: str
    type: str  # 'bet_placed', 'bet_won', 'bet_lost', 'challenge_start', 'balance_adjustment'
    amount: float
    balance_before: float
    balance_after: float
    bet_id: Optional[str]
    description: str
    created_at: str


def wallet_to_dict(wallet: Wallet) -> Dict[str, Any]:
    """Convert Wallet to dictionary for storage/JSON"""
    return asdict(wallet)


def dict_to_wallet(data: Dict[str, Any]) -> Wallet:
    """Convert dictionary to Wallet object"""
    return Wallet(**data)


def transaction_to_dict(transaction: Transaction) -> Dict[str, Any]:
    """Convert Transaction to dictionary for storage/JSON"""
    return asdict(transaction)


def dict_to_transaction(data: Dict[str, Any]) -> Transaction:
    """Convert dictionary to Transaction object"""
    return Transaction(**data)


def create_new_wallet(user_id: str, challenge_type: str, custom_balance: Optional[float] = None) -> Wallet:
    """
    Create a new wallet for a user based on challenge type.
    
    Args:
        user_id: Firebase user ID
        challenge_type: Type of challenge (from ChallengeType enum)
        custom_balance: Optional custom starting balance (only for FREE_PLAY)
    
    Returns:
        New Wallet object
    """
    if challenge_type not in CHALLENGE_CONFIGS:
        raise ValueError(f"Invalid challenge type: {challenge_type}")
    
    config = CHALLENGE_CONFIGS[challenge_type]
    
    # For free play, use custom balance or default
    if challenge_type == ChallengeType.FREE_PLAY:
        starting_balance = custom_balance if custom_balance is not None else 10000.0
        starting_balance = min(starting_balance, config.max_balance)
        target_balance = None
    else:
        starting_balance = config.starting_balance
        target_balance = config.target_balance
    
    now = datetime.utcnow().isoformat()
    
    return Wallet(
        user_id=user_id,
        balance=starting_balance,
        challenge_type=challenge_type,
        starting_balance=starting_balance,
        target_balance=target_balance,
        created_at=now,
        updated_at=now,
        total_wagered=0.0,
        total_won=0.0,
        total_lost=0.0,
        bets_placed=0,
        bets_won=0,
        bets_lost=0
    )


def validate_wallet(wallet_data: Dict[str, Any]) -> bool:
    """Validate wallet data has required fields"""
    required_fields = ['user_id', 'balance', 'challenge_type', 'starting_balance']
    return all(field in wallet_data for field in required_fields)


def get_all_challenge_configs():
    """Get all available challenge configurations"""
    return [asdict(config) for config in CHALLENGE_CONFIGS.values()]
