from flask import Request
from werkzeug.exceptions import BadRequest


def handling_get_file(filename: str, req: Request):
    try:
        f = req.files[filename]
        return f
    except Exception as _:
        raise BadRequest('file with name "file" is required')
