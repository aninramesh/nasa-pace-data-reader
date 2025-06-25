"""
Custom exceptions for the NASA PACE Data Reader library.
"""

class PACEException(Exception):
    """Base exception class for this library."""
    pass

class InstrumentMismatchError(PACEException):
    """Raised when the file instrument does not match the expected instrument."""
    pass

class VariableNotFoundError(PACEException):
    """Raised when a required variable is not found in the data file."""
    pass

class InvalidFileError(PACEException):
    """Raised when a file is not a valid or readable data file."""
    pass
