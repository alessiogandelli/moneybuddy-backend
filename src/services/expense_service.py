"""Simple expense service"""
from models import Expense

class ExpenseService:
    """Lightweight expense service for hackathons"""
    
    def __init__(self):
        # Sample expense data
        self.expenses = [
            Expense(25.50, "food", "Grocery shopping", "2025-09-18", 1),
            Expense(45.00, "transport", "Gas fill-up", "2025-09-17", 2),
            Expense(15.99, "entertainment", "Movie ticket", "2025-09-16", 3),
            Expense(120.75, "utilities", "Electricity bill", "2025-09-15", 4),
            Expense(8.50, "food", "Coffee shop", "2025-09-19", 5),
        ]
        self._next_id = 6
    
    def get_expenses(self, category=None, limit=None, offset=0):
        """Get expenses with optional filtering"""
        expenses = self.expenses.copy()
        
        # Filter by category if specified
        if category:
            expenses = [exp for exp in expenses if exp.category.lower() == category.lower()]
        
        # Sort by date (most recent first)
        expenses.sort(key=lambda x: x.date, reverse=True)
        
        # Apply pagination
        if offset > 0:
            expenses = expenses[offset:]
        if limit:
            expenses = expenses[:limit]
        
        return {
            "expenses": [exp.to_dict() for exp in expenses],
            "total_count": len(expenses)
        }
    
    def create_expense(self, data):
        """Create a new expense"""
        expense = Expense(
            amount=data.get('amount', 0),
            category=data.get('category', ''),
            description=data.get('description', ''),
            date=data.get('date'),
            expense_id=self._next_id
        )
        
        # Validate
        is_valid, error_message = expense.is_valid()
        if not is_valid:
            raise ValueError(error_message)
        
        self.expenses.append(expense)
        self._next_id += 1
        
        return expense.to_dict()
    
    def get_expense_by_id(self, expense_id):
        """Get expense by ID"""
        for expense in self.expenses:
            if expense.id == expense_id:
                return expense.to_dict()
        return None
    
    def update_expense(self, expense_id, data):
        """Update an expense"""
        for expense in self.expenses:
            if expense.id == expense_id:
                if 'amount' in data:
                    expense.amount = float(data['amount'])
                if 'category' in data:
                    expense.category = data['category']
                if 'description' in data:
                    expense.description = data['description']
                if 'date' in data:
                    expense.date = data['date']
                
                # Validate updated expense
                is_valid, error_message = expense.is_valid()
                if not is_valid:
                    raise ValueError(error_message)
                
                return expense.to_dict()
        return None
    
    def delete_expense(self, expense_id):
        """Delete an expense"""
        for i, expense in enumerate(self.expenses):
            if expense.id == expense_id:
                del self.expenses[i]
                return True
        return False
    
    def get_expenses_summary(self):
        """Get expense summary"""
        if not self.expenses:
            return {"total_expenses": 0, "total_amount": 0.0}
        
        total_amount = sum(exp.amount for exp in self.expenses)
        
        # Group by categories
        categories = {}
        for expense in self.expenses:
            if expense.category not in categories:
                categories[expense.category] = {"count": 0, "total_amount": 0.0}
            categories[expense.category]["count"] += 1
            categories[expense.category]["total_amount"] += expense.amount
        
        return {
            "total_expenses": len(self.expenses),
            "total_amount": round(total_amount, 2),
            "categories": categories,
            "recent_expenses": [exp.to_dict() for exp in sorted(self.expenses, key=lambda x: x.date, reverse=True)[:3]]
        }