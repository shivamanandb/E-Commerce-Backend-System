from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Exception raised when a requested resource is not found."""
    def __init__(self, message: str = "Not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class UnauthorizedException(HTTPException):
    """Exception raised when user is not authorized."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


class InvalidNameException(HTTPException):
    """Exception raised when a name is invalid or improperly formatted."""
    def __init__(self, message: str = "Invalid Name"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)


class EmailAlreadyExistsException(HTTPException):
    """Exception raised when trying to register with an existing email."""
    def __init__(self, message: str = "Email already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class UserNotFoundException(HTTPException):
    """Exception raised when a user is not found in the database."""
    def __init__(self, message: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class InvalidPasswordException(HTTPException):
    """Exception raised when the provided password is invalid."""
    def __init__(self, message: str = "Invalid password"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


class ProductNotFoundException(HTTPException):
    """Exception raised when a product is not found."""
    def __init__(self, message: str = "Product not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class InvalidTokenException(HTTPException):
    """Exception raised when a token is invalid or tampered."""
    def __init__(self, message: str = "Invalid token"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)


class InvalidCredentialsException(HTTPException):
    """Exception raised when user credentials are invalid."""
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


class AuthException(HTTPException):
    """Exception raised when a user lacks permission to access a resource."""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


class InvalidStockException(HTTPException):
    """Exception raised when the requested stock quantity is invalid."""
    def __init__(self, message: str = "Invalid stock quantity"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)


class OrderNotFoundException(HTTPException):
    """Exception raised when an order is not found."""
    def __init__(self, message: str = "Order not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class GeneralException(HTTPException):
    """Generic exception for unexpected errors."""
    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=message)
