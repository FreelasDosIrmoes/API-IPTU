from werkzeug.exceptions import *
from flask import *


def handling_get_file(filename : str, request : Request):
    f = None
    try:
        f = request.files[filename]
        return f
    except Exception as e:
        raise BadRequest('file with name "file" is required')