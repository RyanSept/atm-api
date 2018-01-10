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
            print("Expired token.")
            abort(401, message={"Authorization":
                                "Token Expired. Please log in again."})
        except jwt.InvalidTokenError:
            print("Invalid token.")
            abort(401, message={"Authorization":
                                "Invalid Token. Please log in again."})
    return wrapped_view
