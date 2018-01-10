"""
This module contains the resource for getting the account balance
"""

from flask_restful import Resource


class Balance(Resource):
    def get(self):
        return "WOOOOOO"
