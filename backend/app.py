#!/usr/bin/env python3
"""
Main application entry point for Render deployment
"""
from app import create_app
import os

# Create the Flask app instance
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)