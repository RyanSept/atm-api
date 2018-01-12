from api.tests import BaseTestCase
import json


class AccountBalanceTestSuite(BaseTestCase):
    def test_can_get_account_balance(self):
        """
        Test can get account balance
        """
        self.create_test_account()
        self.add_auth_to_headers()
        response = self.client.get("/accounts/balance",
                                   headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.get_data())
        self.assertEquals(data, {'balance': 100000,
                          'account_number': '11223344'})
