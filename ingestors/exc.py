ENCRYPTED_MSG = "The document might be protected with a password. Try removing the password protection and re-uploading the documents."


class ProcessingException(Exception):
    "A data-related error occuring during file processing."
    pass


class UnauthorizedError(Exception):
    """Raised when a document is protected by a password and can not be parsed."""

    pass
