from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, message: str = "Not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        
class UnautorizedException(HTTPException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
        
class InvalidNameException(HTTPException):
    def __init__(self, message: str = "Invalid Name"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)