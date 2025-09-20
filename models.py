from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

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