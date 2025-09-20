"""Budget management endpoints"""
from flask import Blueprint, jsonify, request
from services.budget_service import BudgetService

budget_bp = Blueprint('budget', __name__)
budget_service = BudgetService()

@budget_bp.route('/budget', methods=['GET'])
def get_budget():
    """Get current budget overview"""
    try:
        budget_data = budget_service.get_budget_overview()
        return jsonify(budget_data)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve budget: {str(e)}"}), 500

@budget_bp.route('/budget/categories', methods=['GET'])
def get_budget_categories():
    """Get budget breakdown by categories"""
    try:
        categories = budget_service.get_categories_breakdown()
        return jsonify({"categories": categories})
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve categories: {str(e)}"}), 500

@budget_bp.route('/budget', methods=['POST'])
def create_budget():
    """Create or update budget"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        result = budget_service.create_or_update_budget(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create budget: {str(e)}"}), 500

@budget_bp.route('/budget/categories/<category_name>', methods=['PUT'])
def update_category_budget(category_name):
    """Update budget for a specific category"""
    try:
        data = request.get_json()
        if not data or 'amount' not in data:
            return jsonify({"error": "Amount is required"}), 400
        
        result = budget_service.update_category_budget(category_name, data['amount'])
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update category budget: {str(e)}"}), 500