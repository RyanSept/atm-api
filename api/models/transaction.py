"""
This module contains the model for the transactions table
"""
from api import db
from sqlalchemy.sql import func


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.BigInteger, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id",
                                                     ondelete='CASCADE'))
    date_created = db.Column(db.DateTime(timezone=True),
                             server_default=func.now())

    def __init__(self, amount, account_id):
        self.amount = amount
        self.account_id = account_id
