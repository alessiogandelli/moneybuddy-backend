from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

from models import db, Transaction

# Create Flask app
app = Flask(__name__)
CORS(app)

# SQLite config - simplest possible
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hackathon-key'

# Initialize SQLAlchemy with app
db.init_app(app)

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