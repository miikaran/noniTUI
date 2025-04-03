from fastapi import HTTPException

class NoniAPIException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail={"error": detail})

class UnauthorizedException(NoniAPIException):
    def __init__(self, detail: str = "Unauthorized. Session ID might be missing"):
        super().__init__(status_code=401, detail=detail)

class BadRequestException(NoniAPIException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=400, detail=detail)

class NotFoundException(NoniAPIException):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=404, detail=detail)

class ConflictException(NoniAPIException):
    def __init__(self, detail: str = "Conflict Occurred"):
        super().__init__(status_code=409, detail=detail)

class InternalServerException(NoniAPIException):
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(status_code=500, detail=detail)