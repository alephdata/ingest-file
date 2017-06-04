

class IngestorException(Exception):
    pass


class ConfigurationException(IngestorException):
    "Errors in the configuration of the ingestors (e.g. missing settings)."
    pass


class SystemException(IngestorException):
    "Errors caused by external failures (e.g. missing external dependencies)."
    pass


class ProcessingException(IngestorException):
    "A data-related error occuring during file processing."
    pass
