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
        
class EmailAlreadyExistsException(HTTPException):
    def __init__(self, message: str = "Email Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)
        

class UserNotFoundException(HTTPException):
    def __init__(self, message: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class InvalidPasswordException(HTTPException):
    def __init__(self, message: str = "Invalid Password"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,detail=message)
        
class ProductNotFoundException(HTTPException):
    def __init__(self, message: str = "Product not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        
class UserNotFoundException(HTTPException):
    def __init__(self, message: str = "User not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        
class InvalidTokenException(HTTPException):
    def __init__(self, message: str = "Invalid token"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)
    
class InvalidCredentialsException(HTTPException):
    def __init__(self, message: str = "Could not validate Credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
        
class AuthException(HTTPException):
    def __init__(self, message: str = "Permission Denied"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)

class InvalidStockException(HTTPException):
    def __init__(self, message: str = "Permission Denied"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)