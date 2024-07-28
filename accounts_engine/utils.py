import os
import re
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)
logger_info = logging.getLogger("info")
logger_error = logging.getLogger("error")


def success_true_response(message=None, data=None, count=None):
    result = dict(success=True)
    result["message"] = message or ""
    result["data"] = data or {}
    if count is not None:
        result["count"] = count
    return result


def success_false_response(message=None, data=None):
    result = dict(success=False)
    result["message"] = message or ""
    result["data"] = data or {}

    return result


def remove_special_char(string):
    string = re.sub("[^A-Za-z0-9]+", "", string)
    return string


def has_country_code(phone_number):
    # Regular expression pattern to match country codes
    country_code_pattern = r"^\+\d+"

    # Use re.match to check if the pattern matches the beginning of the phone number
    match = re.match(country_code_pattern, phone_number)

    # If a match is found, it has a country code; otherwise, it doesn't
    return bool(match)
