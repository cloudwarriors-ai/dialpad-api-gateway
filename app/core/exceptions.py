from fastapi import HTTPException, status


class CustomException(HTTPException):
    """Base exception class for custom exceptions"""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class DatabaseException(CustomException):
    """Exception for database errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransformationError(CustomException):
    """Exception for transformation errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class ValidationError(CustomException):
    """Exception for validation errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class FieldMappingError(CustomException):
    """Exception for field mapping errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class NotFoundError(CustomException):
    """Exception for resource not found errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class AuthenticationError(CustomException):
    """Exception for authentication errors"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(CustomException):
    """Exception for authorization errors"""
    def __init__(self, detail=str):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)