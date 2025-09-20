"""Expense management endpoints"""
from flask import Blueprint, jsonify, request
from services.expense_service import ExpenseService

expenses_bp = Blueprint('expenses', __name__)
expense_service = ExpenseService()

@expenses_bp.route('/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses with optional filtering"""
    try:
        # Get query parameters for filtering
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int, default=0)
        
        expenses = expense_service.get_expenses(
            category=category, 
            limit=limit, 
            offset=offset
        )
        return jsonify(expenses)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve expenses: {str(e)}"}), 500

@expenses_bp.route('/expenses', methods=['POST'])
def create_expense():
    """Create a new expense"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        expense = expense_service.create_expense(data)
        return jsonify({
            "message": "Expense created successfully",
            "expense": expense
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create expense: {str(e)}"}), 500

@expenses_bp.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """Get a specific expense by ID"""
    try:
        expense = expense_service.get_expense_by_id(expense_id)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify(expense)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve expense: {str(e)}"}), 500

@expenses_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update an existing expense"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        expense = expense_service.update_expense(expense_id, data)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
            
        return jsonify({
            "message": "Expense updated successfully",
            "expense": expense
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update expense: {str(e)}"}), 500

@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense"""
    try:
        success = expense_service.delete_expense(expense_id)
        if not success:
            return jsonify({"error": "Expense not found"}), 404
            
        return jsonify({"message": "Expense deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete expense: {str(e)}"}), 500

@expenses_bp.route('/expenses/summary', methods=['GET'])
def get_expenses_summary():
    """Get expense summary statistics"""
    try:
        summary = expense_service.get_expenses_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve summary: {str(e)}"}), 500