from api.app import *


def handling_get_file(filename: str, req: Request):
    f = None
    try:
        f = req.files[filename]
        return f
    except Exception as e:
        raise BadRequest('file with name "file" is required')
