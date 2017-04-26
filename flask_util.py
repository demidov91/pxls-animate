from flask import request
import datetime
from utils import GifBuilder

import defines

API_DETAILING_TO_INTERNAL = {
    'low': GifBuilder.DETAILING_LOW,
    'medium': GifBuilder.DETAILING_MEDIUM,
    'high': GifBuilder.DETAILING_HIGH,
}


def get_flask_datetime(arg_name):
    date_string = request.args.get(arg_name)
    if not date_string:
        return None

    return datetime.datetime.strptime(date_string, defines.API_DATETIME_FORMAT)


def get_coordinates(arg_name):
    arg_string = request.args.get(arg_name)
    if arg_string:
        return tuple(int(x) for x in arg_string.split('-'))

    x = request.args.get(arg_name + '-x')
    y = request.args.get(arg_name + '-y')
    if not (x and y):
        return

    return int(x), int(y)


def get_flask_float(arg_name):
    arg = request.args.get(arg_name)
    if not arg:
        return None

    return float(arg)


def get_flask_detailing(arg_name):
    arg = request.args.get(arg_name)
    if not arg:
        return None

    return API_DETAILING_TO_INTERNAL[arg]


def get_flask_arg(arg_name):
    """
    Just a helper to call requests.args.get(arg_name)
    """
    return request.args.get(arg_name)