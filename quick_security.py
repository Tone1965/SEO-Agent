"""
Quick Security Implementation for SEO-Agent
Adds basic protection before deployment
"""
import os
from functools import wraps
from flask import request, jsonify
import hashlib
import time

# Simple API key authentication
MASTER_API_KEY = os.getenv('MASTER_API_KEY', 'change-this-immediately')

def require_api_key(f):
    """Decorator to require API key for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        if api_key != MASTER_API_KEY:
            return jsonify({'error': 'Invalid API key'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Rate limiting (simple in-memory)
request_counts = {}

def rate_limit(max_requests=60, window=60):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = int(time.time())
            window_start = current_time - window
            
            # Clean old entries
            if client_ip in request_counts:
                request_counts[client_ip] = [
                    timestamp for timestamp in request_counts[client_ip]
                    if timestamp > window_start
                ]
            else:
                request_counts[client_ip] = []
            
            # Check rate limit
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Add current request
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Input validation
def validate_input(required_fields):
    """Decorator to validate required fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.json:
                return jsonify({'error': 'JSON body required'}), 400
            
            missing = []
            for field in required_fields:
                if field not in request.json:
                    missing.append(field)
            
            if missing:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing': missing
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Security headers middleware
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# CORS configuration
def configure_cors(app):
    """Configure CORS for production"""
    @app.after_request
    def after_request(response):
        # Only allow specific origins in production
        allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
        origin = request.headers.get('Origin')
        
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-API-Key'
        
        return add_security_headers(response)

# Apply security to Flask app
def secure_app(app):
    """Apply all security measures to Flask app"""
    
    # Set secure session config
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Configure CORS
    configure_cors(app)
    
    # Add global rate limiting
    @app.before_request
    @rate_limit(max_requests=100, window=60)
    def global_rate_limit():
        pass
    
    return app

# Example usage in main.py:
"""
from quick_security import secure_app, require_api_key, validate_input

# Secure the app
app = secure_app(app)

# Protect endpoints
@app.route('/api/generate', methods=['POST'])
@require_api_key
@validate_input(['business_type', 'location'])
def generate_website():
    # Your code here
"""