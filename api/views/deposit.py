"""
This module contains the resource for depositing funds into an account
"""

from flask_restful import Resource, reqparse
from flask import request
from api import db
from api.models.account import Account
from api.models.transaction import Transaction
from api.utils import auth


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
            # number deposits exceeded
            if len(todays_deposits) >= account.max_deposit_frequency:
                print("Deposit frequency limit exceeded.")
                return {"message":
                        {"deposit_amount": "The allowed maximum number of"
                         " deposits per day for your account is {}".format(
                             account.max_deposit_frequency)}}, 400
            sum_todays_deposits = sum(
                deposit.amount for deposit in todays_deposits)
            # this deposit would exceed the daily limit
            if sum_todays_deposits + request_json.deposit_amount >\
                    account.max_deposit_per_day:
                print("Deposit amount limit for day exceeded.")
                return {"message":
                        {"deposit_amount": "Unable to make deposit as "
                         "it would exceed your"
                         " daily deposit limit of {}."
                         " You have deposited {} today".format(
                             account.max_deposit_per_day,
                             sum_todays_deposits)}}, 400

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
