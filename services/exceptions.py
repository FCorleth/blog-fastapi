class NotFoundError(Exception):
    def __init__(self, detail: str = "Not found"):
        self.detail = detail
        super().__init__(detail)

class ConflictError(Exception):
    def __init__(self, detail: str = "Conflict"):
        self.detail = detail
        super().__init__(detail)
    
class BadRequestError(Exception):
    def __init__(self, detail: str = "Bad request"):
        self.detail = detail
        super().__init__(detail)

class UnauthorizedError(Exception):
    def __init__(self, detail: str = "Unauthorized"):
        self.detail = detail
        super().__init__(detail)