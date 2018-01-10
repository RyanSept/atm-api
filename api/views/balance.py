"""
This module contains the resource for getting the account balance
"""

from flask_restful import Resource
from api import db
from api.models.account import Account


class Balance(Resource):
    def get(self):
        return "Balance"
