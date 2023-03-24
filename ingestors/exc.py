class ProcessingException(Exception):
    "A data-related error occuring during file processing."
    pass


class UnauthorizedError(Exception):
    """Raised when a document is protected by a password and can not be parsed."""

    pass
