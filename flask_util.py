from flask import request
import datetime

import defines


def get_flask_datetime(arg_name):
    date_string = request.args.get(arg_name)
    if not date_string:
        return None

    return datetime.datetime.strptime(date_string, defines.API_DATETIME_FORMAT)


def get_flask_pair(arg_name):
    arg_string = request.args.get(arg_name)
    if not arg_string:
        return None

    return tuple(int(x) for x in arg_string.split('-'))


def get_flask_arg(arg_name):
    """
    Just a helper to call requests.args.get(arg_name)
    """
    return request.args.get(arg_name)