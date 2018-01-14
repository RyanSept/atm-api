from api import create_app, rest_api, db
from api.config import load_config
from api.models.account import Account
import unittest
import json
import logging

app = create_app(load_config())
logging.disable(logging.CRITICAL)


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def tearDown(self):
        rest_api.resources = []

    def create_test_account(self):
        """
        Create account in db for testing
        """
        if not hasattr(self, "headers"):
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
        self.client.post("/accounts/create",
                         data=json.dumps(self.account),
                         headers=self.headers)

    def add_auth_to_headers(self):
        """
        Login and add Authorization headers
        """
        if not hasattr(self, "headers"):
            self.headers = {"Content-Type": "application/json"}

        login = {"account_number": self.account["account_number"],
                 "pin": self.account["pin"]}
        token = json.loads(self.client.post(
            "/accounts/login",
            data=json.dumps(login),
            headers=self.headers).get_data())["token"]
        self.headers["Authorization"] = "Bearer " + token
