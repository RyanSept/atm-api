"""
This module contains the resource for getting the account balance
"""

from flask_restful import Resource
from flask import request
from api import db
from api.models.account import Account
from api.utils import auth


class Balance(Resource):
    @auth
    def get(self):
        account_id = request.authorization["account_id"]
        # get account
        account = db.session.query(Account.account_number,
                                   Account.balance).filter_by(
            id=account_id).first()
        print("Retrieved balance for account %s" % account.account_number)
        return {"balance": account.balance,
                "account_number": account.account_number}
