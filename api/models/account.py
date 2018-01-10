"""
This module contains the model for the accounts table
"""
from api import db
from sqlalchemy.sql import func


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(255), unique=True)
    pin = db.Column(db.Integer, nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    balance = db.Column(db.BigInteger, nullable=False)
    # could use normalization
    account_type = db.Column(db.String(10), default="bronze")

    max_withdraw_per_day = db.Column(db.Integer, default=50000)
    max_withdraw_per_transaction = db.Column(db.Integer, default=20000)
    max_withdraw_frequency = db.Column(db.Integer, default=3)

    max_deposit_per_day = db.Column(db.Integer, default=150000)
    max_deposit_per_transaction = db.Column(db.Integer, default=40000)
    max_deposit_frequency = db.Column(db.Integer, default=4)
    date_created = db.Column(db.DateTime(timezone=True),
                             server_default=func.now())
    date_modified = db.Column(db.DateTime(timezone=True),
                              server_default=func.now(),
                              onupdate=func.now())

    transactions = db.relationship('Transaction', backref='transaction',
                                   lazy=True)

    def __init__(self, account_number, pin, first_name, last_name,
                 opening_balance):
        self.account_number = account_number
        self.pin = pin
        self.first_name = first_name
        self.last_name = last_name
        self.balance = opening_balance
