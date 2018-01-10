"""
This module contains the resource for getting the account balance
"""

from flask_restful import Resource
from flask import request
from api import db
from api.models.account import Account
from api.utils import auth


class Balance(Resource):
    @auth
    def get(self):
        return "Balance"
