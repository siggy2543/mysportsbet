"""
Logging configuration for structured logging
"""
import logging
import sys
from typing import Any
from datetime import datetime
import json

from core.config import settings

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        return json.dumps(log_entry, default=str)

def setup_logging() -> logging.Logger:
    """Setup application logging configuration"""
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Set formatter
    if settings.DEBUG:
        # Use simple formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        # Use JSON formatter for production
        formatter = JSONFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    # Reduce noise from external libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    # Create application logger
    app_logger = logging.getLogger("sports_betting")
    app_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    return app_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(f"sports_betting.{name}")

# Custom log methods
def log_user_action(logger: logging.Logger, user_id: int, action: str, details: Any = None):
    """Log user actions with context"""
    extra = {"user_id": user_id}
    message = f"User action: {action}"
    if details:
        message += f" - {details}"
    logger.info(message, extra=extra)

def log_api_call(logger: logging.Logger, api_name: str, endpoint: str, status_code: int, response_time: float):
    """Log external API calls"""
    extra = {
        "api_name": api_name,
        "endpoint": endpoint,
        "status_code": status_code,
        "response_time": response_time
    }
    message = f"API call to {api_name}: {endpoint} - {status_code} ({response_time:.3f}s)"
    
    if status_code >= 400:
        logger.warning(message, extra=extra)
    else:
        logger.info(message, extra=extra)

def log_bet_placement(logger: logging.Logger, user_id: int, bet_type: str, stake: float, odds: float):
    """Log bet placements"""
    extra = {
        "user_id": user_id,
        "bet_type": bet_type,
        "stake": stake,
        "odds": odds,
        "potential_payout": stake * odds
    }
    message = f"Bet placed: {bet_type} - ${stake} @ {odds}"
    logger.info(message, extra=extra)

def log_prediction(logger: logging.Logger, model_version: str, event_id: int, prediction: str, confidence: float):
    """Log ML predictions"""
    extra = {
        "model_version": model_version,
        "event_id": event_id,
        "prediction": prediction,
        "confidence": confidence
    }
    message = f"Prediction made: {prediction} (confidence: {confidence:.2f})"
    logger.info(message, extra=extra)