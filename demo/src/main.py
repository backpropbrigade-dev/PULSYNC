"""
PULSYNC Application Root Entrypoint
Delegates to backend.app.main:app for unified service execution and backwards compatibility.
"""
from backend.app.main import app

__all__ = ["app"]
