"""
This module contains the view for creating a new account
"""
from flask_restful import Resource, reqparse
from passlib.hash import pbkdf2_sha256
from api import db
from api.models.account import Account
import sqlalchemy


class Register(Resource):
    def post(self):
        # parse request json
        parser = reqparse.RequestParser()
        parser.add_argument("account_number", location="json", required=True)
        parser.add_argument("pin", location="json",
                            type=self._validate_pin,
                            required=True)
        parser.add_argument("first_name", location="json",
                            type=self._validate_str,
                            required=True)
        parser.add_argument("last_name", location="json",
                            type=self._validate_str,
                            required=True)
        parser.add_argument("opening_balance", location="json", type=int,
                            required=True)
        request_json = parser.parse_args()

        try:
            # create account
            account = Account(
                request_json["account_number"],
                pbkdf2_sha256.hash(request_json["pin"]),
                request_json["first_name"],
                request_json["last_name"],
                request_json["opening_balance"]
            )
            db.session.add(account)
            db.session.commit()
            return {"message": "Profile was created."}, 201
        except sqlalchemy.exc.IntegrityError as error:
            if "duplicate key value" in str(error):
                return {"message": "Unable to create account."}, 400
        except Exception as error:
            print(error)
            return {"message": "Something went wrong"}, 500

    def _validate_pin(self, pin):
        pin = str(pin)
        if pin.isdigit() and len(pin) == 4:
            return pin
        raise ValueError("Invalid pin number: {}. Expected 4 digit pin".format(
            pin))

    def _validate_str(self, string):
        if len(string):
            return string
        raise ValueError("Value cannot be empty.")
