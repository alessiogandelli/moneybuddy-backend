"""Simple utilities for the API"""
import os
from flask import Flask, jsonify

def create_app():
    """Create Flask app with simple configuration"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.getenv("SUPER_SECRET_KEY", "hackathon-secret-key")
    app.config['DEBUG'] = os.getenv('FLASK_ENV') == 'development'
    
    # Enable CORS if available
    try:
        from flask_cors import CORS
        CORS(app)
    except ImportError:
        pass
    
    # Register API routes
    from api import api_bp
    app.register_blueprint(api_bp)
    
    # Simple error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Server error"}), 500
    
    # Welcome route
    @app.route('/')
    def home():
        return jsonify({
            "message": "Welcome to MoneyBuddy API! 💰",
            "version": "1.0.0",
            "endpoints": ["/api/health", "/api/budget", "/api/expenses"]
        })
    
    return app