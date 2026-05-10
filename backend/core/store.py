"""
Central in-memory signal store — single source of truth for all APIs.
Updated for Sniper Mode with Cooldown tracking.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Shared in-memory stores
signal_store: List[Dict[str, Any]] = []
scanner_state: List[Dict[str, Any]] = []
last_signal_times: Dict[str, datetime] = {}

def add_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
    symbol = signal["symbol"]
    signal["id"] = len(signal_store) + 1
    signal["created_at"] = datetime.utcnow().isoformat()
    signal["outcome"] = None
    
    signal_store.append(signal)
    last_signal_times[symbol] = datetime.utcnow()
    
    if len(signal_store) > 100:
        signal_store.pop(0)
    return signal

def is_in_cooldown(symbol: str, cooldown_minutes: int = 90) -> bool:
    """
    Checks if a pair is currently in the sniper cooldown period.
    """
    if symbol not in last_signal_times:
        return False
    
    elapsed = datetime.utcnow() - last_signal_times[symbol]
    return elapsed < timedelta(minutes=cooldown_minutes)

def set_scanner_state(state: List[Dict[str, Any]]):
    global scanner_state
    scanner_state = state

def get_scanner_state() -> List[Dict[str, Any]]:
    return scanner_state

def get_signals(limit: int = 50) -> List[Dict[str, Any]]:
    return list(reversed(signal_store[-limit:]))
