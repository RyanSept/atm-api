from api.tests import BaseTestCase
from api import db
from api.models.account import Account
import json


class AccountWithdrawTestSuite(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.create_test_account()
        self.add_auth_to_headers()
        self.withdraw = {"withdrawal_amount": 10000}
        with self.app.app_context():
            self.account = db.session.query(Account).filter_by(
                account_number=self.account["account_number"]).first()

    def test_can_withdraw_successfully(self):
        """
        Test can withdraw successfully
        """
        response = self.client.post("/accounts/withdraw",
                                    data=json.dumps(self.withdraw),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())

        self.assertEqual(data, {"message": "Withdrew 10000 successfully.",
                                "new_balance": 90000})

    def test_cannot_withdraw_more_than_account_balance(self):
        """
        Test cannot withdraw more than account balance
        """
        # change account balance
        with self.app.app_context():
            db.session.query(Account).filter_by(
                account_number=self.account.account_number).update(
                {"balance": 1500})
            db.session.commit()

        # attempt withdraw 10000
        response = self.client.post("/accounts/withdraw",
                                    data=json.dumps(self.withdraw),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data())

        self.assertEqual(data, {"message":
                                {"withdrawal_amount": "You do not have enough"
                                 " balance in your account to withdraw 10000. "
                                 "The bank requires a minumum balance of 1000"
                                 " for the account to remain open."}})

    def test_cannot_withdraw_more_than_20000_at_once(self):
        """
        Test cannot withdraw more than transaction limit
        """
        self.withdraw["withdrawal_amount"] = \
            self.account.max_withdraw_per_transaction + 1
        response = self.client.post("/accounts/withdraw",
                                    data=json.dumps(self.withdraw),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.get_data())
        self.assertEqual(data,
                         {"message": {
                             "withdrawal_amount": "The maximum withdrawal per"
                             " transaction is 20000. The minimum is 1."}})

    def test_cannot_withdraw_negative_amount(self):
        """
        Test cannot withdraw negative amount
        """
        self.withdraw["withdrawal_amount"] = -1000
        response = self.client.post("/accounts/withdraw",
                                    data=json.dumps(self.withdraw),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.get_data())
        self.assertEqual(data,
                         {"message": {
                             "withdrawal_amount": "The maximum withdrawal per"
                             " transaction is 20000. The minimum is 1."}})

    def test_cannot_withdraw_more_times_than_frequency_limit(self):
        """
        Test cannot withdraw more times than frequency limit
        """
        # exhaust withdrawals
        for i in range(self.account.max_withdraw_frequency):
            response = self.client.post("/accounts/withdraw",
                                        data=json.dumps(self.withdraw),
                                        headers=self.headers)
            self.assertEqual(response.status_code, 200,
                             msg="Unable to make withdrawal.")

        # make extra withdrawal
        response = self.client.post("/accounts/withdraw",
                                    data=json.dumps(self.withdraw),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data())

        self.assertEqual(data, {
                         "message": {
                             "withdrawal_amount": "The allowed maximum number"
                             " of withdrawals per day for your account is 3"}})

    def test_cannot_withdraw_more_than_daily_total_limit(self):
        """
        Test cannot withdraw more money than is allowed for a day
        """
        self.withdraw["withdrawal_amount"] = 20000
        # exhaust withdrawal amount i.e withdraw 40,000, 2 times
        for i in range(2):
            response = self.client.post("/accounts/withdraw",
                                        data=json.dumps(self.withdraw),
                                        headers=self.headers)
            self.assertEqual(response.status_code, 200,
                             msg="Unable to make withdrawal.")

        """
        Attempt to withdraw 20,000 third time should fail since daily
        withdrawal total would be 60,000
        """
        response = self.client.post("/accounts/withdraw",
                                    data=json.dumps(self.withdraw),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data())
        self.assertEqual(data, {
                         "message": {
                             "withdrawal_amount": "Unable to make withdrawal"
                             " as it would exceed your daily withdrawal limit"
                             " of 50000. You have made withdrawals amounting"
                             " to 40000 today"}})
