"""
This module contains the view for a user login/session creation
"""
from flask_restful import reqparse, Resource
from api import db
from api.models.account import Account
from flask import current_app

import datetime
import jwt


class Login(Resource):
    def post(self):
        # parse request json
        parser = reqparse.RequestParser()
        parser.add_argument("account_number", location="json", required=True)
        parser.add_argument("pin", location="json", type=int, required=True)
        request_json = parser.parse_args()
        account = db.session.query(Account.id,
                                   Account.pin).filter_by(
            account_number=request_json.account_number).first()

        if account is not None and account.pin == int(request_json["pin"]):
            token = jwt.encode(
                {
                    "account_id": account.id,
                    "user_key": acc,
                    "iat": datetime.datetime.utcnow(),
                    "exp": datetime.datetime.utcnow() +
                    datetime.timedelta(
                        minutes=current_app.config["JWT_TOKEN_EXPIRY"])
                }, current_app.config["SECRET_KEY"], algorithm='HS256')

            return {"token": token.decode("utf-8")}

        return {"message": "Invalid pin."}, 401
