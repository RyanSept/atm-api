from api.tests import BaseTestCase
from api import db
from api.models.account import Account
import json


class AccountDepositTestSuite(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.create_test_account()
        self.add_auth_to_headers()
        self.deposit = {"deposit_amount": 10000}
        with self.app.app_context():
            self.account = db.session.query(Account).filter_by(
                account_number=self.account["account_number"]).first()

    def test_can_deposit_successfully(self):
        """
        Test can deposit successfully
        """
        response = self.client.post("/accounts/deposit",
                                    data=json.dumps(self.deposit),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data())

        self.assertEqual(data, {"message": "Deposited 10000 successfully.",
                                "new_balance": 110000})

    def test_cannot_deposit_more_than_40000_at_once(self):
        """
        Test cannot deposit more than transaction limit
        """
        self.deposit["deposit_amount"] = \
            self.account.max_deposit_per_transaction + 1
        response = self.client.post("/accounts/deposit",
                                    data=json.dumps(self.deposit),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.get_data())
        self.assertEqual(data,
                         {"message": {
                             "deposit_amount": "The maximum deposit per"
                             " transaction is 40000. The minimum is 1."}})

    def test_cannot_deposit_negative_amount(self):
        """
        Test cannot deposit negative amount
        """
        self.deposit["deposit_amount"] = -1000
        response = self.client.post("/accounts/deposit",
                                    data=json.dumps(self.deposit),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.get_data())
        self.assertEqual(data,
                         {"message": {
                             "deposit_amount": "The maximum deposit per"
                             " transaction is 40000. The minimum is 1."}})

    def test_cannot_deposit_more_times_than_frequency_limit(self):
        """
        Test cannot deposit more times than frequency limit
        """
        # exhaust deposits
        for i in range(self.account.max_deposit_frequency):
            response = self.client.post("/accounts/deposit",
                                        data=json.dumps(self.deposit),
                                        headers=self.headers)
            self.assertEqual(response.status_code, 200,
                             msg="Unable to make deposit.")

        # make extra deposit
        response = self.client.post("/accounts/deposit",
                                    data=json.dumps(self.deposit),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data())

        self.assertEqual(data, {
                         "message": {
                             "deposit_amount": "The allowed maximum number of"
                             " deposits per day for your account is 4"}})

    def test_cannot_deposit_more_than_daily_total_limit(self):
        """
        Test cannot deposit more money than is allowed for a day
        """
        self.deposit["deposit_amount"] = 40000
        # exhaust deposit amount i.e deposit 40,000, 3 times
        for i in range(3):
            response = self.client.post("/accounts/deposit",
                                        data=json.dumps(self.deposit),
                                        headers=self.headers)
            self.assertEqual(response.status_code, 200,
                             msg="Unable to make deposit.")

        """
        Attempt to deposit 40,000 fourth time should fail since daily deposit
        total would be 160,000
        """
        response = self.client.post("/accounts/deposit",
                                    data=json.dumps(self.deposit),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data())
        self.assertEqual(data, {
                         "message": {
                             "deposit_amount": "Unable to make deposit as it"
                             " would exceed your daily deposit limit of"
                             " 150000. You have made deposits amounting to"
                             " 120000 today"}})
