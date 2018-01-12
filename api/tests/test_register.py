from api.tests import BaseTestCase
from api import db
from api.models.account import Account
import json


class RegisterTestSuite(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.headers = {"Content-Type": "application/json"}
        self.account = {
            "account_number": "11223344",
            "pin": "1234",
            "first_name": "John",
            "last_name": "Doe",
            "opening_balance": 100000
        }
        with self.app.app_context():
            db.session.query(Account.account_number).filter_by(
                account_number=self.account["account_number"]).delete()
            db.session.commit()

    def test_creates_account(self):
        """
        Test can successfully create account
        """
        response = self.client.post("/accounts/create",
                                    data=json.dumps(self.account),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.get_data())

        self.assertEqual(data, {"message": "Account was created."})

    def test_validates_pin(self):
        """
        Test attempt to create account with invalid pin format
        """
        self.account["pin"] = "awoaowdja"
        response = self.client.post("/accounts/create",
                                    data=json.dumps(self.account),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data())
        self.assertEqual(data, {"message":
                                {"pin": "Invalid pin number: awoaowdja."
                                 " Expected 4 digit pin"}})

    def test_does_not_create_duplicate_account(self):
        """
        Test returns an error upon duplicate account creation attempt
        """
        # create account once
        response = self.client.post("/accounts/create",
                                    data=json.dumps(self.account),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 201)

        # attempt creation a second time
        response = self.client.post("/accounts/create",
                                    data=json.dumps(self.account),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data())
        self.assertEqual(data, {"message": "Account already exists."})
