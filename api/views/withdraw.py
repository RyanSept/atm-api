"""
This module contains the resource for withdrawing funds from an account
"""

from flask_restful import Resource, reqparse
from flask import request
from api import db
from api.models.account import Account
from api.models.transaction import Transaction
from api.utils import auth, validate_transaction_frequency,\
    validate_transaction_limit


class Withdraw(Resource):
    @auth
    def post(self):
        account_id = request.authorization["account_id"]
        account = Account.query.filter_by(
            id=account_id).first()

        # parse request body arguments
        parser = reqparse.RequestParser()
        parser.add_argument("withdrawal_amount", location="json",
                            required=True,
                            type=lambda val:
                            self._validate_withdrawal_amount(val, account))
        request_json = parser.parse_args()

        print("Retrieving today's withdrawals for account: %s" % account.id)
        todays_withdrawals = account.get_todays_withdrawals()
        if todays_withdrawals:
            # check if number of withdrawals exceeded
            validate_transaction_frequency(
                todays_withdrawals,
                account.max_withdraw_frequency,
                "withdrawal")

            sum_todays_withdrawals = sum(abs(withdrawal.amount)
                                         for withdrawal in todays_withdrawals)
            # check if this withdrawal would exceed the daily limit
            validate_transaction_limit(
                sum_todays_withdrawals,
                request_json.withdrawal_amount,
                account.max_withdraw_per_day,
                "withdrawal")

        print("Withdrawing %s from account." % request_json.withdrawal_amount)
        # increase account balance and record transaction
        account.balance -= request_json.withdrawal_amount
        transaction = Transaction(-request_json.withdrawal_amount, account.id)
        account.transactions.append(transaction)
        db.session.add(account, transaction)
        db.session.commit()
        return {
            "message": "Withdrew {} successfully.".format(
                request_json.withdrawal_amount),
            "new_balance": account.balance
        }

    def _validate_withdrawal_amount(self, withdrawal_amount, account):
        if not type(withdrawal_amount) is int:
            raise ValueError("Should be an integer.")

        if withdrawal_amount > account.max_withdraw_per_transaction\
                or withdrawal_amount < 1:
            raise ValueError("The maximum withdrawal per transaction is {}."
                             " The minimum is 1.".format(
                                 account.max_withdraw_per_transaction))

        if account.balance - withdrawal_amount < 1000:
            raise ValueError("You do not have enough balance"
                             " in your account to withdraw {}. "
                             "The bank requires a minumum balance"
                             " of 1000 for the account to remain open.".format(
                                 withdrawal_amount))
        return withdrawal_amount
