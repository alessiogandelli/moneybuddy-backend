#!/usr/bin/env python3
"""
Simple test to verify the API works
"""
import sys
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(current_dir))

def test_api():
    """Test the API structure"""
    try:
        print("🧪 Testing API imports...")
        
        # Test models
        from models import Expense, Budget
        print("✅ Models imported successfully")
        
        # Test services
        from services.budget_service import BudgetService
        from services.expense_service import ExpenseService
        print("✅ Services imported successfully")
        
        # Test API blueprints
        from api import api_bp
        from api.health import health_bp
        from api.budget import budget_bp
        from api.expenses import expenses_bp
        print("✅ API blueprints imported successfully")
        
        # Test utils
        from utils import create_app
        print("✅ Utils imported successfully")
        
        # Test app creation
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test services functionality
        budget_service = BudgetService()
        expense_service = ExpenseService()
        
        budget_data = budget_service.get_budget_overview()
        expense_data = expense_service.get_expenses()
        
        print(f"✅ Budget service: {len(budget_data['categories'])} categories")
        print(f"✅ Expense service: {expense_data['total_count']} expenses")
        
        # Test models
        test_expense = Expense(50.0, "food", "Test expense")
        is_valid, _ = test_expense.is_valid()
        print(f"✅ Expense model validation: {is_valid}")
        
        test_budget = Budget(1000.0)
        test_budget.add_category("test", 100.0)
        print("✅ Budget model working")
        
        print("\n🎉 API is ready to run!")
        print("Run: python src/main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api()