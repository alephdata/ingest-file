import sys
import traceback
import os.path
import logging
from datetime import datetime


class States:
    """Available ingestor states."""
    #: Initiated, but no processing was done yet.
    NEW = u'new'
    #: Initiated and the processing was started, but not finished.
    STARTED = u'started'
    #: The ingestor processing ended.
    FINISHED = u'finished'
    #: All available states.
    ALL = [NEW, STARTED, FINISHED]


class Statuses:
    """Available ingestor statuses."""
    #: Indicates that during the processing no errors or failures occured.
    SUCCESS = u'success'
    #: Indicates occurance of errors during the processing.
    FAILURE = u'failure'
    #: Indicates a complete ingestor stop due to system issue.
    STOPPED = u'stopped'
    #: All available statuses.
    ALL = [SUCCESS, FAILURE, STOPPED]


class Result(dict):
    """Generic ingestor result class.

    Mainly a dict implementation with object like getters/setters.
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, *args, **kwargs):
        """Generic ingestor result class constructor.

        Initializes some of the attributes:

        - ``mime_type``, guessed MIME type of the file
        - ``file_size``, the size of the file
        - ``checksum``, the SHA digest of the file
        - ``title``, the title of the document (optional)
        - ``authors``, a list of the document authors (if any)
        - ``content``, the document body, usually text
        - ``order``, the order or page (if available)

        """

        self.mime_type = None
        self.file_size = None
        self.checksum = None
        self.title = None
        self.authors = []
        self.content = None
        self.order = 0

        super(Result, self).__init__(self, *args, **kwargs)


class Ingestor(object):
    """Generic ingestor class."""

    #: Result object factory class.
    RESULT_CLASS = Result
    #: List of MIME types it handles.
    MIME_TYPES = []
    #: Available states.
    STATES = States
    #: Available statuses.
    STATUSES = Statuses
    #: A list of exception types leading to a failure status.
    FAILURE_EXCEPTIONS = [
        TypeError,
        ValueError,
        ArithmeticError,
        AssertionError
    ]

    def __init__(self, fio, file_path, parent=None):
        """Generic ingestor constructor class.

        :param :py:class:`io.FileIO` fio: An instance of the file to process.
        :param str file_path: The file path.
        :param :py:class:`Ingestor` parent: An instance of the parent ignestor.
        """
        self.fio = fio
        self.file_path = os.path.realpath(file_path)
        self.parent = parent
        self.children = []
        self.state = States.NEW
        self.status = Statuses.SUCCESS
        self.started_at = datetime.utcnow()
        self.ended_at = None
        self.logger = logging.getLogger(self.__module__)
        self.failure_exceptions = tuple(self.FAILURE_EXCEPTIONS)

        self.result = Result()

    def configure(self):
        """Ingestor configuration endpoint.

        Initializes different aspects of the ingestor.
        Returns a dictionary with configuration values.

        A good example where to use it, is to overwrite the implementation and
        provide external calls to ``os.environ`` to fetch different variables
        or resolve system paths for executables.

        :rtype: dict
        """
        return {}

    def before(self):
        """Callback called before the processing starts."""
        pass

    def after(self):
        """Callback called after the processing starts."""
        pass

    def before_child(self):
        """Callback called before the processing of a child file starts."""
        pass

    def after_child(self):
        """Callback called after the processing of a child starts."""
        pass

    def exception_handler(self, exception=None):
        """Ingestor error handler."""
        self.log_exception()

    def log_exception(self):
        """Extract and log the latest exception."""
        lines = traceback.format_exception(*sys.exc_info())
        self.logger.error('\n'.join(lines))

    def ingest(self, config):
        """The ingestor implementation. Should be overwritten.

        This method does not return anything.
        Use the ``result`` attribute to store any resulted data.

        :param dict config: A dictionary with settings.
        """
        raise NotImplemented()

    def run(self):
        """Main execution loop of an ingestor."""
        self.state = States.STARTED
        config = self.configure()

        try:
            self.before()
            self.ingest(config)
        except Exception as exception:
            self.exception_handler(exception)

            if isinstance(exception, self.failure_exceptions):
                self.status = Statuses.FAILURE
            else:
                self.status = Statuses.STOPPED
        finally:
            self.state = States.FINISHED
            self.after()
