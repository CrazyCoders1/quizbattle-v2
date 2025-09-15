"""
WSGI entry point for QuizBattle production deployment
"""
import os
from app import create_app

# Create Flask application instance
app = create_app()

if __name__ == "__main__":
    # This is only used for development
    app.run(host='0.0.0.0', port=5000, debug=False)