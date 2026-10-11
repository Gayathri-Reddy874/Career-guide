# wsgi.py - WSGI entry point for Gunicorn
import sys
import os
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import your Flask app
from app import app 

# Optional: For production logging
import logging

# Configure logging for production
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'Career Guide AI is running'}

# The application object is named 'application' for Gunicorn