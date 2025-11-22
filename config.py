import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    
    # Use SQLite for offline functionality
    # Force SQLite even if DATABASE_URL is set to PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'sqlite:///stockmaster.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLite-specific settings for better concurrency
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'check_same_thread': False,  # Allow multi-threaded access
            'timeout': 20  # Timeout for database locks
        }
    }
    
    ITEMS_PER_PAGE = 20
    LOW_STOCK_DAYS_THRESHOLD = 7
    
    REPLIT_AUTH_ENABLED = True
