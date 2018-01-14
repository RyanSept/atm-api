"""
This module contains the resource for depositing funds into an account
"""

from flask_restful import Resource, reqparse
from flask import request
from api import db
from api.models.account import Account
from api.models.transaction import Transaction
from api.utils import auth, validate_transaction_frequency,\
    validate_transaction_limit


class Deposit(Resource):
    @auth
    def post(self):
        account_id = request.authorization["account_id"]
        account = Account.query.filter_by(
            id=account_id).first()

        # parse request body arguments
        parser = reqparse.RequestParser()
        parser.add_argument("deposit_amount", location="json", required=True,
                            type=lambda val:
                            self._validate_deposit_amount(val, account))
        request_json = parser.parse_args()

        print("Retrieving today's deposits for account: %s" % account.id)
        todays_deposits = account.get_todays_deposits()
        if todays_deposits:
            # check if number deposits exceeded
            validate_transaction_frequency(
                todays_deposits,
                account.max_deposit_frequency,
                "deposit")
            sum_todays_deposits = sum(
                deposit.amount for deposit in todays_deposits)
            # check if this deposit would exceed the daily limit
            validate_transaction_limit(
                sum_todays_deposits,
                request_json.deposit_amount,
                account.max_deposit_per_day,
                "deposit")

        print("Depositing %s to account." % request_json.deposit_amount)
        # increase account balance and record transaction
        account.balance += request_json.deposit_amount
        transaction = Transaction(request_json.deposit_amount, account.id)
        account.transactions.append(transaction)
        db.session.add(account, transaction)
        db.session.commit()
        return {
            "message": "Deposited {} successfully.".format(
                request_json.deposit_amount),
            "new_balance": account.balance
        }

    def _validate_deposit_amount(self, deposit_amount, account):
        if not type(deposit_amount) is int:
            raise ValueError("Should be an integer.")
        if deposit_amount <= account.max_deposit_per_transaction\
                and deposit_amount > 0:
            return deposit_amount
        raise ValueError("The maximum deposit per transaction is {}."
                         " The minimum is 1.".format(
                             account.max_deposit_per_transaction))
