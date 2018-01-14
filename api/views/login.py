"""
This module contains the view for a user login/session creation
"""
from flask_restful import reqparse, Resource
from api import db
from api.models.account import Account
from flask import current_app
from passlib.hash import pbkdf2_sha256


import datetime
import jwt


class Login(Resource):
    def post(self):
        # parse request json
        parser = reqparse.RequestParser()
        parser.add_argument("account_number", location="json", required=True)
        parser.add_argument("pin", location="json", required=True)
        request_json = parser.parse_args()
        account = db.session.query(Account.id,
                                   Account.pin).filter_by(
            account_number=request_json.account_number).first()

        if account is None:
            current_app.logger.info(
                "Invalid account number: %s", request_json.account_number)
            return {"message": "Invalid account number."}, 401

        try:
            pin_is_valid = pbkdf2_sha256.verify(request_json["pin"],
                                                account.pin)
            if not pin_is_valid:
                current_app.logger.debug("Pin is invalid.")
                return {"message": "Pin is invalid."}, 401

            token = jwt.encode(
                {
                    "account_id": account.id,
                    "iat": datetime.datetime.utcnow(),
                    "exp": datetime.datetime.utcnow() +
                    datetime.timedelta(
                        minutes=current_app.config["JWT_TOKEN_EXPIRY"])
                }, current_app.config["SECRET_KEY"], algorithm='HS256')

            return {"token": token.decode("utf-8")}
        except ValueError as error:
            if "not a valid pbkdf2_sha256 hash" in str(error):
                current_app.logger.error("Invalid hash stored as pin.")
            current_app.logger.error(error)
            return {"message": "Something went wrong."}, 500
