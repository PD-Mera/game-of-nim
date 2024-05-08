class CustomException(Exception):
    """Build custom exception"""

    def __cstr__(self):
        return f"[{self.__class__.__name__}]: {self.__str__()}!!!"

class TupleLengthMismatch(CustomException):
    """Raised when length of 2 tuple is not equal."""

class InvalidPile(CustomException):
    """Raised when the pile is invalid."""

class InvalidNumber(CustomException):
    """Raised when the number is invalid."""