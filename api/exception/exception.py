class ExceptionResponse(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message, self.code)

class BadRequest(ExceptionResponse):
    def __init__(self, message):
        self.message = message
        self.code = 400
        super().__init__(self.message, self.code)

class NotFound(ExceptionResponse):
    def __init__(self, message):
        self.message = message
        self.code = 404
        super().__init__(self.message, self.code)
