from functools import wraps
from flask import request, current_app
from flask_restful import abort

import jwt


def auth(view_function):
    """
    Decorator for checking if the token is provided in the Authorization header
    and if it is valid

    :param view_function: The view function to wrap
    :return: wrapped view
    """
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        token = None
        # check token present in headers and is using Bearer schema
        if "Authorization" in request.headers and\
                request.headers["Authorization"].find("Bearer ") is 0:
            token = request.headers["Authorization"][7:]

        if token is None:
            abort(401, message={"Authorization":
                                "Authorization token required. Hint: Make sure"
                                " you're using the 'Bearer' schema."})

        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithm="HS256")
            request.authorization = payload
            return view_function(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            current_app.logger.info("Expired token: %s", token)
            abort(401, message={"Authorization":
                                "Token Expired. Please log in again."})
        except jwt.InvalidTokenError:
            current_app.logger.info("Invalid token.")
            abort(401, message={"Authorization":
                                "Invalid Token. Please log in again."})
    return wrapped_view


def validate_transaction_frequency(transaction_list,
                                   transaction_frequency_limit,
                                   transaction_type):
    """
    Check if transaction frequency has been exceeded. Abort if so, return
    false if not

    :param transaction_list: a list of the current day's transactions
    :type transaction_list: list

    :param transaction_frequency_limit: max transactions per day
    :type transaction_frequency_limit: int

    :param transaction_type: type of transaction eg. "withdraw" or "deposit"
    :type transaction_type: str

    :return: boolean
    """
    current_app.logger.debug("Got %s %ss for today.", len(
        transaction_list), transaction_type)
    if len(transaction_list) >= transaction_frequency_limit:
        current_app.logger.info(
            f"{transaction_type.title()} frequency limit exceeded.")
        abort(400, message={
              f"{transaction_type}_amount": f"The allowed maximum number of"
              f" {transaction_type}s per day for your"
              f" account is {transaction_frequency_limit}"})
    return False


def validate_transaction_limit(sum_todays_transactions,
                               pending_transaction_amount,
                               transaction_amount_limit,
                               transaction_type):
    """
    Check if max transaction amount for day will be reached if
    current pending transaction is fulfilled

    :param sum_todays_transactions: sum of the current day's transactions
    :type sum_todays_transactions: int

    :param pending_transaction_amount: amount to be added
    :type pending_transaction_amount: int

    :param transaction_amount_limit: max transaction amount
    :type transaction_amount_limit: int

    :param transaction_type: type of transaction eg. "withdraw" or "deposit"
    :type transaction_type: str

    :return: boolean
    """
    if sum_todays_transactions + pending_transaction_amount >\
            transaction_amount_limit:
        current_app.logger.info(
            f"{transaction_type.title()} amount limit for day exceeded.")
        abort(400, message={
              f"{transaction_type}_amount": f"Unable to make"
              f" {transaction_type} as it would exceed your"
              f" daily {transaction_type} limit of {transaction_amount_limit}."
              f" You have made {transaction_type}s"
              f" amounting to {sum_todays_transactions} today"})
    return False
