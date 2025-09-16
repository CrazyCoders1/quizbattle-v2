"""
Database utility functions for connection resilience and error handling
"""
import functools
import time
from flask import current_app
from app import db
from sqlalchemy.exc import DisconnectionError, OperationalError, TimeoutError


def db_retry(max_retries=3, backoff_factor=1):
    """
    Decorator to retry database operations on connection failures
    
    Args:
        max_retries (int): Maximum number of retry attempts
        backoff_factor (int): Multiplier for exponential backoff
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except (DisconnectionError, OperationalError, TimeoutError) as e:
                    last_exception = e
                    if attempt == max_retries:
                        current_app.logger.error(f"❌ DB operation failed after {max_retries} retries: {str(e)}")
                        break
                        
                    # Exponential backoff
                    sleep_time = backoff_factor * (2 ** attempt)
                    current_app.logger.warning(f"⚠️ DB operation failed (attempt {attempt + 1}), retrying in {sleep_time}s: {str(e)}")
                    
                    # Try to rollback and refresh connection
                    try:
                        db.session.rollback()
                        db.session.close()
                    except:
                        pass
                    
                    time.sleep(sleep_time)
                    
                except Exception as e:
                    # Non-connection errors should not be retried
                    current_app.logger.error(f"❌ DB operation failed with non-retryable error: {str(e)}")
                    raise
                    
            # If all retries failed, raise the last exception
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def ensure_db_connection():
    """
    Ensure database connection is alive, reconnect if necessary
    """
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return True
    except Exception as e:
        current_app.logger.warning(f"⚠️ Database connection lost, attempting to reconnect: {str(e)}")
        try:
            db.session.rollback()
            db.session.close()
            db.session.execute(text('SELECT 1'))
            current_app.logger.info("✅ Database connection restored")
            return True
        except Exception as reconnect_error:
            current_app.logger.error(f"❌ Failed to restore database connection: {str(reconnect_error)}")
            return False


def safe_db_commit():
    """
    Safely commit database changes with error handling
    """
    try:
        db.session.commit()
        return True, None
    except Exception as e:
        current_app.logger.error(f"❌ Database commit failed: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False, str(e)


def get_db_stats():
    """
    Get database connection pool statistics
    """
    try:
        engine = db.get_engine()
        pool = engine.pool
        
        return {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalid': pool.invalid()
        }
    except Exception as e:
        current_app.logger.error(f"❌ Failed to get DB stats: {str(e)}")
        return None