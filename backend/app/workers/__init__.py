"""
Background workers for automated tasks
"""
from .email_poller import start_background_polling, stop_background_polling

__all__ = ["start_background_polling", "stop_background_polling"]
