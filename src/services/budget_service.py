"""Simple budget service"""
from models import Budget

class BudgetService:
    """Lightweight budget service for hackathons"""
    
    def __init__(self):
        # Initialize with sample data
        self.budget = Budget(total_budget=5000.0)
        self.budget.add_category("food", 1500.0)
        self.budget.add_category("transport", 800.0)
        self.budget.add_category("entertainment", 600.0)
        self.budget.add_category("utilities", 1200.0)
        self.budget.add_category("shopping", 900.0)
        
        # Add some sample spending
        self.budget.add_expense_to_category("food", 850.25)
        self.budget.add_expense_to_category("transport", 450.0)
        self.budget.add_expense_to_category("entertainment", 320.50)
        self.budget.add_expense_to_category("utilities", 729.75)
    
    def get_budget_overview(self):
        """Get complete budget overview"""
        return self.budget.to_dict()
    
    def get_categories_breakdown(self):
        """Get categories breakdown"""
        return self.budget.to_dict()['categories']
    
    def create_or_update_budget(self, data):
        """Create or update budget"""
        if 'total_budget' in data:
            if data['total_budget'] <= 0:
                raise ValueError("Total budget must be greater than 0")
            self.budget.total_budget = float(data['total_budget'])
        
        if 'categories' in data:
            for cat_name, cat_data in data['categories'].items():
                if 'budget' in cat_data:
                    budget_amount = float(cat_data['budget'])
                    if budget_amount < 0:
                        raise ValueError(f"Budget for {cat_name} cannot be negative")
                    self.budget.add_category(cat_name, budget_amount)
        
        return {
            "message": "Budget updated successfully",
            "budget": self.budget.to_dict()
        }
    
    def update_category_budget(self, category_name, amount):
        """Update budget for a specific category"""
        if amount < 0:
            raise ValueError("Budget amount cannot be negative")
        
        self.budget.add_category(category_name, amount)
        
        return {
            "message": f"Budget for {category_name} updated successfully",
            "category": self.budget.get_category_info(category_name)
        }
    
    def add_expense_to_category(self, category_name, amount):
        """Add expense to category"""
        self.budget.add_expense_to_category(category_name, amount)