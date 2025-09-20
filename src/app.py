from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import json
import os

# Create Flask app
app = Flask(__name__)
CORS(app)

# SQLite config - simplest possible
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hackathon-key'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Transaction model - matches your frontend object
class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trx_id = db.Column(db.String(100), nullable=False)
    
    # Account info
    account_iban = db.Column(db.String(50))
    account_name = db.Column(db.String(100))
    account_currency = db.Column(db.String(10))
    
    # Customer info
    customer_name = db.Column(db.String(100))
    product = db.Column(db.String(50))
    
    # Transaction classification
    trx_type = db.Column(db.String(50))
    booking_type = db.Column(db.String(50))
    
    # Dates
    value_date = db.Column(db.DateTime)
    booking_date = db.Column(db.DateTime)
    
    # Financial details
    direction = db.Column(db.String(20), nullable=False)  # debit/credit or IN/OUT
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    
    # Merchant info
    merchant_name = db.Column(db.String(100))
    merchant_full_text = db.Column(db.Text)
    merchant_phone = db.Column(db.String(50))
    merchant_address = db.Column(db.Text)
    merchant_iban = db.Column(db.String(50))
    
    # Card and payment
    card_id_masked = db.Column(db.String(50))
    acquirer_country = db.Column(db.String(10))
    reference_nr = db.Column(db.String(100))
    
    # Metadata
    raw_payload = db.Column(db.Text)  # Store as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trxId': self.trx_id,
            'accountIban': self.account_iban,
            'accountName': self.account_name,
            'accountCurrency': self.account_currency,
            'customerName': self.customer_name,
            'product': self.product,
            'trxType': self.trx_type,
            'bookingType': self.booking_type,
            'valueDate': self.value_date.isoformat() if self.value_date else None,
            'bookingDate': self.booking_date.isoformat() if self.booking_date else None,
            'direction': self.direction,
            'amount': self.amount,
            'currency': self.currency,
            'merchantName': self.merchant_name,
            'merchantFullText': self.merchant_full_text,
            'merchantPhone': self.merchant_phone,
            'merchantAddress': self.merchant_address,
            'merchantIban': self.merchant_iban,
            'cardIdMasked': self.card_id_masked,
            'acquirerCountry': self.acquirer_country,
            'referenceNr': self.reference_nr,
            'rawPayload': json.loads(self.raw_payload) if self.raw_payload else None,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }

# THE ONLY ENDPOINT YOU NEED
@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if request.method == 'GET':
        # Get all transactions
        transactions = Transaction.query.all()
        return jsonify([t.to_dict() for t in transactions])
    
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

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=420)