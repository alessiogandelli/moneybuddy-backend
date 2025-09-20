# MoneyBuddy API 💰

A well-structured Flask API for personal budget management, designed for hackathons with clean architecture and simple but powerful features.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Poetry (recommended) or pip

### Installation

1. **Install dependencies:**
   ```bash
   poetry install
   # or
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the API:**
   ```bash
   python src/main.py
   # or
   poetry run python src/main.py
   ```

The API will be available at `http://localhost:5000`

## 📁 Project Structure

```
src/
├── main.py              # Application entry point
├── utils/               # Application factory and utilities
│   └── __init__.py      # Flask app creation, middleware, error handlers
├── api/                 # API endpoints (Flask Blueprints)
│   ├── __init__.py      # Blueprint registration
│   ├── health.py        # Health check endpoints
│   ├── budget.py        # Budget management endpoints
│   └── expenses.py      # Expense tracking endpoints
├── models/              # Data models and validation
│   └── __init__.py      # ExpenseModel, BudgetModel, etc.
└── services/            # Business logic layer
    ├── budget_service.py    # Budget operations
    └── expense_service.py   # Expense operations
```

## 🛠 API Endpoints

### Health Check
- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed health with system info

### Budget Management
- `GET /api/budget` - Get budget overview
- `GET /api/budget/categories` - Get category breakdown
- `POST /api/budget` - Create/update budget
- `PUT /api/budget/categories/{category}` - Update category budget

### Expense Tracking
- `GET /api/expenses` - Get expenses (with filtering & pagination)
- `POST /api/expenses` - Create new expense
- `GET /api/expenses/{id}` - Get specific expense
- `PUT /api/expenses/{id}` - Update expense
- `DELETE /api/expenses/{id}` - Delete expense
- `GET /api/expenses/summary` - Get expense statistics


# MoneyBuddy API 💰

**A simple, hackathon-ready Flask API for personal budget management.**

Clean, lightweight, and easy to use - perfect for rapid development!

## 🚀 Quick Start

```bash
# Install dependencies
poetry install
# OR with pip:
pip install flask flask-cors python-dotenv

# Run the API
python src/main.py
```

That's it! API runs on `http://localhost:5000` 🎉

## 📁 Simple Structure

```
src/
├── main.py              # Start here - entry point
├── utils/              # App setup
├── api/                # Endpoints (health, budget, expenses)
├── models/             # Simple data classes (Expense, Budget)
└── services/           # Business logic
```

## 🛠 API Endpoints

### Budget Management
- `GET /api/budget` - Get budget overview
- `POST /api/budget` - Create/update budget
- `PUT /api/budget/categories/{category}` - Update category budget

### Expense Tracking
- `GET /api/expenses` - Get all expenses
- `POST /api/expenses` - Add new expense
- `GET /api/expenses/{id}` - Get specific expense
- `PUT /api/expenses/{id}` - Update expense
- `DELETE /api/expenses/{id}` - Delete expense
- `GET /api/expenses/summary` - Get statistics

### Health Check
- `GET /api/health` - Health status

## 📊 Example Usage

### Create Budget
```bash
curl -X POST http://localhost:5000/api/budget \
  -H "Content-Type: application/json" \
  -d '{
    "total_budget": 2000,
    "categories": {
      "food": {"budget": 600},
      "transport": {"budget": 300}
    }
  }'
```

### Add Expense
```bash
curl -X POST http://localhost:5000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 25.50,
    "category": "food",
    "description": "Groceries"
  }'
```

## 🧪 Test It

```bash
python test_structure.py
```

## 🔧 Environment Variables

Create `.env` file:
```env
FLASK_ENV=development
PORT=5000
SUPER_SECRET_KEY=your-secret-key
```

## ✨ Hackathon Features

✅ **Zero setup** - No database needed  
✅ **Sample data** - Ready to demo  
✅ **CORS enabled** - Frontend friendly  
✅ **Simple code** - Easy to understand  
✅ **Fast to extend** - Add features quickly  

## 🚀 Deploy Anywhere

- **Local**: `python src/main.py`
- **Heroku**: Ready to deploy
- **Railway**: Zero config deployment
- **Any cloud**: Standard Flask app

---

**Built for speed. Perfect for hackathons. 🏆**


## install a new package

```bash
poetry add <package_name>
```
what you usually do with ```pip install pandas``` is now ```poetry add pandas```

## using .env file

if you have to handle sensitive data put it in the ```.env ```file, it will be ignored by git and you can access it with ```os.getenv('VARIABLE_NAME')```


## suggestion 
open the folder with vscode and you should see 
```#%%``` lines, these are the cell division, you can run a cell with ```shift+enter``` or pressing the play button on the left of the cell.



if something breaks reclone the repo and start over, it's a good practice to have a clean environment to work with.

```bash