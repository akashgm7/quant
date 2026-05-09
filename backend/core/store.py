"""
Central in-memory signal store — single source of truth for all APIs.
No database required; signals are held in memory and broadcast via WebSocket.
"""
from typing import List, Dict, Any
from datetime import datetime
import asyncio

# Shared in-memory stores
signal_store: List[Dict[str, Any]] = []
scanner_state: List[Dict[str, Any]] = []

def add_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
    signal["id"] = len(signal_store) + 1
    signal["created_at"] = datetime.utcnow().isoformat()
    signal["outcome"] = None
    signal["journal_notes"] = None
    signal_store.append(signal)
    # Keep last 100 signals
    if len(signal_store) > 100:
        signal_store.pop(0)
    return signal

def update_signal(signal_id: int, update_data: Dict[str, Any]) -> Dict[str, Any] | None:
    for sig in signal_store:
        if sig["id"] == signal_id:
            sig.update(update_data)
            return sig
    return None

def get_signals(limit: int = 50) -> List[Dict[str, Any]]:
    return list(reversed(signal_store[-limit:]))

def set_scanner_state(state: List[Dict[str, Any]]):
    global scanner_state
    scanner_state.clear()
    scanner_state.extend(state)

def get_scanner_state() -> List[Dict[str, Any]]:
    return scanner_state
