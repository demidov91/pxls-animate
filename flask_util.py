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

    return arg_string.split('-')