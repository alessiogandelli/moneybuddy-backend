from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import logging
import re
from typing import Dict, Any

from models import db, Transaction

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for development - restrict in production

# SQLite config - simplest possible
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hackathon-key'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

# Initialize SQLAlchemy with app
db.init_app(app)

# THE ONLY ENDPOINT YOU NEED
@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    # get all transactions
    if request.method == 'GET':
        # Get all transactions
        transactions = Transaction.query.all()
        return jsonify([t.to_dict() for t in transactions])
    
    # add a new transaction
    elif request.method == 'POST':
        # Add new transaction
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse dates if provided
        value_date = None
        booking_date = None
        if data.get('valueDate'):
            try:
                value_date = datetime.fromisoformat(data['valueDate'].replace('Z', '+00:00'))
            except:
                pass
        
        if data.get('bookingDate'):
            try:
                booking_date = datetime.fromisoformat(data['bookingDate'].replace('Z', '+00:00'))
            except:
                pass
        
        # Create transaction
        transaction = Transaction(
            trx_id=data.get('trxId', ''),
            account_iban=data.get('accountIban'),
            account_name=data.get('accountName'),
            account_currency=data.get('accountCurrency'),
            customer_name=data.get('customerName'),
            product=data.get('product'),
            trx_type=data.get('trxType'),
            booking_type=data.get('bookingType'),
            value_date=value_date,
            booking_date=booking_date,
            direction=data.get('direction', 'OUT'),
            amount=float(data.get('amount', 0)),
            currency=data.get('currency', 'EUR'),
            merchant_name=data.get('merchantName'),
            merchant_full_text=data.get('merchantFullText'),
            merchant_phone=data.get('merchantPhone'),
            merchant_address=data.get('merchantAddress'),
            merchant_iban=data.get('merchantIban'),
            card_id_masked=data.get('cardIdMasked'),
            acquirer_country=data.get('acquirerCountry'),
            reference_nr=data.get('referenceNr'),
            raw_payload=json.dumps(data.get('rawPayload')) if data.get('rawPayload') else None
        )
        
        try:
            db.session.add(transaction)
            db.session.commit()
            return jsonify(transaction.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# DELETE specific transaction by ID
@app.route('/transaction/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        # Find the transaction by ID
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Delete the transaction
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Simple AI Chat Service for Financial Assistant
class FinancialChatBot:
    """Simple rule-based chatbot for financial assistance"""
    
    def __init__(self):
        self.greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        self.financial_keywords = {
            "spending": ["spending", "spent", "expense", "expenses", "cost", "costs"],
            "income": ["income", "salary", "earnings", "revenue"],
            "budget": ["budget", "budgeting", "financial plan"],
            "savings": ["save", "saving", "savings"],
            "transactions": ["transaction", "transactions", "payment", "payments"],
            "analysis": ["analyze", "analysis", "report", "summary", "overview"]
        }
    
    def get_response(self, message: str) -> str:
        """Generate AI-like response based on user message"""
        message_lower = message.lower().strip()
        
        # Handle greetings
        if any(greeting in message_lower for greeting in self.greetings):
            return "Hello! I'm your MoneyBuddy financial assistant. I can help you analyze your spending, track transactions, and provide budgeting advice. What would you like to know about your finances?"
        
        # Handle transaction-related queries
        if any(keyword in message_lower for keyword in self.financial_keywords["transactions"]):
            try:
                transaction_count = Transaction.query.count()
                if transaction_count > 0:
                    recent_transactions = Transaction.query.order_by(Transaction.booking_date.desc()).limit(5).all()
                    total_spent = sum(t.amount for t in recent_transactions if t.direction == 'OUT')
                    return f"You have {transaction_count} transactions in total. Your last 5 transactions show spending of €{total_spent:.2f}. Would you like me to analyze your spending patterns?"
                else:
                    return "I don't see any transactions in your account yet. Once you add some transactions, I can help you analyze your spending patterns!"
            except Exception:
                return "I can help you manage your transactions. Try adding some transactions first, and I'll provide insights about your spending!"
        
        # Handle spending analysis
        if any(keyword in message_lower for keyword in self.financial_keywords["spending"]):
            try:
                outgoing_transactions = Transaction.query.filter_by(direction='OUT').all()
                if outgoing_transactions:
                    total_spent = sum(t.amount for t in outgoing_transactions)
                    avg_transaction = total_spent / len(outgoing_transactions)
                    return f"Based on your transactions, you've spent €{total_spent:.2f} total with an average transaction of €{avg_transaction:.2f}. Your largest expense was €{max(t.amount for t in outgoing_transactions):.2f}."
                else:
                    return "I don't see any spending transactions yet. Once you add some expenses, I can provide detailed spending analysis!"
            except Exception:
                return "I can analyze your spending patterns once you have some transaction data. Would you like to add some transactions first?"
        
        # Handle budget advice
        if any(keyword in message_lower for keyword in self.financial_keywords["budget"]):
            return "Here are some budgeting tips: 1) Track all expenses, 2) Set spending limits for categories, 3) Review your transactions weekly, 4) Save at least 20% of income, 5) Plan for unexpected expenses. Would you like specific advice based on your spending data?"
        
        # Handle savings questions
        if any(keyword in message_lower for keyword in self.financial_keywords["savings"]):
            return "Great question about savings! I recommend the 50/30/20 rule: 50% for needs, 30% for wants, 20% for savings. Based on your transaction history, I can help identify areas where you could save more. What's your current savings goal?"
        
        # Handle help requests
        if "help" in message_lower:
            return "I can help you with: \n• Analyzing your spending patterns\n• Tracking transactions\n• Budgeting advice\n• Savings recommendations\n• Financial insights\n\nJust ask me something like 'How much did I spend?' or 'Give me budgeting tips!'"
        
        # Default helpful response
        return "I'm your MoneyBuddy assistant! I can help analyze your finances, track spending, and provide budgeting advice. Try asking me about your transactions, spending patterns, or financial goals. What would you like to know?"


# Chat endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint that accepts user messages and returns AI responses
    Expected format:
    {
        "message": "User's message here",
        "timestamp": "2025-09-20T10:30:00.000Z"
    }
    """
    print('chat arrivata')
    try:
        # Validate request content type
        if not request.is_json:
            app.logger.warning("Chat request without JSON content-type")
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        if not data:
            app.logger.warning("Chat request with empty data")
            return jsonify({
                'error': 'Request body is required'
            }), 400
        
        if 'message' not in data or not data['message'].strip():
            app.logger.warning("Chat request without message")
            return jsonify({
                'error': 'Message field is required and cannot be empty'
            }), 400
        
        user_message = data['message'].strip()
        timestamp = data.get('timestamp', datetime.utcnow().isoformat() + 'Z')
        
        # Log the incoming request (with 🚀 as specified)
        app.logger.info(f"🚀 Chat Request - Message: {user_message[:100]}... Timestamp: {timestamp}")
        
        # Initialize chatbot and get response
        chatbot = FinancialChatBot()
        ai_response = chatbot.get_response(user_message)
        
        # Prepare response
        response_data = {
            'response': ai_response,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Log successful response (with ✅ as specified)
        app.logger.info(f"✅ Chat Response - Length: {len(ai_response)} chars")
        
        return jsonify(response_data), 200
        
    except json.JSONDecodeError:
        app.logger.error("❌ Chat request with invalid JSON")
        return jsonify({
            'error': 'Invalid JSON format'
        }), 400
        
    except Exception as e:
        # Log the error (with ❌ as specified)
        app.logger.error(f"❌ Chat error: {str(e)}")
        
        return jsonify({
            'response': "Sorry, I'm having trouble connecting right now. Please try again."
        }), 500


# Root endpoint - API documentation
@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        'message': 'MoneyBuddy API',
        'version': '1.0.0',
        'endpoints': {
            '/': 'API documentation (this endpoint)',
            '/api': 'API info',
            '/api/chat': 'POST - Chat with AI financial assistant',
            '/api/health': 'GET - Health check',
            '/transaction': 'GET/POST - Transaction management',
            '/transaction/<id>': 'DELETE - Delete specific transaction'
        },
        'chat_example': {
            'url': '/api/chat',
            'method': 'POST',
            'body': {
                'message': 'How much did I spend this month?',
                'timestamp': '2025-09-20T10:30:00.000Z'
            }
        }
    }), 200

# API info endpoint
@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'MoneyBuddy API',
        'version': '1.0.0',
        'status': 'online',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'available_endpoints': [
            {'path': '/api/chat', 'method': 'POST', 'description': 'Chat with AI assistant'},
            {'path': '/api/health', 'method': 'GET', 'description': 'Health check'},
            {'path': '/transaction', 'method': 'GET/POST', 'description': 'Transaction management'}
        ]
    }), 200

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0'
    }), 200

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=420)