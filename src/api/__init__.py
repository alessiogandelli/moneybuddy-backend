"""API package initialization"""
from flask import Blueprint

# Create a main API blueprint that will contain all API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import and register sub-blueprints
from .health import health_bp
from .budget import budget_bp
from .expenses import expenses_bp

# Register sub-blueprints with the main API blueprint
api_bp.register_blueprint(health_bp)
api_bp.register_blueprint(budget_bp)
api_bp.register_blueprint(expenses_bp)