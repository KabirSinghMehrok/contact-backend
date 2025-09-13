"""Security utilities for API key validation and rate limiting."""

import time
import logging
from typing import Dict, Optional
from fastapi import HTTPException, status
from config import settings

logger = logging.getLogger(__name__)

# Simple in-memory rate limiting (for MVP)
rate_limit_storage: Dict[str, Dict[str, float]] = {}


def validate_api_key(api_key: Optional[str]) -> bool:
    """Validate API key (simple implementation for MVP)."""
    if not api_key:
        return False
    
    # For MVP, accept any non-empty API key
    # In production, you'd validate against a database or external service
    return len(api_key.strip()) > 0


def check_rate_limit(api_key: str) -> bool:
    """Check if API key has exceeded rate limit."""
    current_time = time.time()
    minute_window = int(current_time // 60)
    
    if api_key not in rate_limit_storage:
        rate_limit_storage[api_key] = {}
    
    user_limits = rate_limit_storage[api_key]
    
    # Clean old windows
    for window in list(user_limits.keys()):
        if int(window) < minute_window - 1:  # Keep only current and previous window
            del user_limits[window]
    
    # Check current window
    current_requests = user_limits.get(str(minute_window), 0)
    
    if current_requests >= settings.RATE_LIMIT_PER_MINUTE:
        return False
    
    # Increment counter
    user_limits[str(minute_window)] = current_requests + 1
    return True


def get_api_key_from_header(header: Optional[str]) -> Optional[str]:
    """Extract API key from header."""
    if not header:
        return None
    
    # Handle "Bearer token" format or direct key
    if header.startswith("Bearer "):
        return header[7:]
    return header


async def verify_api_key(api_key: Optional[str]) -> str:
    """Verify API key and check rate limits."""
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    
    if not check_rate_limit(api_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return api_key
