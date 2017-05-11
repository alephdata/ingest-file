import sys
import traceback
import os.path
import logging
import importlib
import inspect
import hashlib
from datetime import datetime

try:
    import magic
except ImportError as error:
    logging.exception(error)


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
        self.file_size = 0
        self.checksum = None
        self.title = None
        self.authors = []
        self.content = None
        self.order = 0

        super(Result, self).__init__(self, *args, **kwargs)

    def extract_file_info(self, fio, file_path, blocksize=65536):
        """Extracts and updates general file info from its data and path.

        :param fio: An instance of the file to process.
        :type fio: py:class:`io.FileIO`
        :param file_path: The file path.
        :type file_path: str
        :param blocksize: The blocksize to read chunks of data.
        :type blocksize: int
        """
        sha_hash = hashlib.sha1()

        for chunk in iter(lambda: fio.read(blocksize), b''):
            sha_hash.update(chunk)

        self.checksum = sha_hash.hexdigest()
        self.file_size = fio.tell()
        self.title = os.path.basename(file_path)

        fio.seek(0)


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

    def __init__(self, fio, file_path, parent=None, mime_type=None):
        """Generic ingestor constructor class.

        :param fio: An instance of the file to process.
        :type fio: py:class:`io.FileIO`
        :param file_path: The file path.
        :type file_path: str
        :param parent: Indicates parent file if this is was part of a composed
                       file. Examples: archives, email files, etc.
        :type parent: :py:class:`Ingestor`
        """
        self.fio = fio
        self.file_path = os.path.realpath(file_path)
        self.parent = parent
        self.children = []
        self.state = States.NEW
        self.status = Statuses.SUCCESS
        self.started_at = None
        self.ended_at = None
        self.logger = logging.getLogger(self.__module__)
        self.failure_exceptions = tuple(self.FAILURE_EXCEPTIONS)

        self.result = Result(mime_type=mime_type)

        # Do not extract file info unless it is a new file
        if mime_type:
            self.result.extract_file_info(self.fio, self.file_path)

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

    def exception_handler(self):
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
        self.before()
        self.started_at = datetime.utcnow()
        config = self.configure()

        try:
            self.ingest(config)
        except Exception as exception:
            self.exception_handler()

            if isinstance(exception, self.failure_exceptions):
                self.status = Statuses.FAILURE
            else:
                self.status = Statuses.STOPPED
        finally:
            self.ended_at = datetime.utcnow()
            self.state = States.FINISHED
            self.after()

    @classmethod
    def find_ingestors(cls, cache=[]):
        """Finds available ingestors and caches the results.

        :return: A list of classes.
        :rtype: list
        """
        if cache:
            return cache

        module = importlib.import_module(__package__)

        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            if inspect.isclass(attr) and issubclass(cls, Ingestor):
                cache.append(attr)

        return cache

    @classmethod
    def match(cls, fio, blocksize=4096):
        """Runs file mime type detection to discover appropriate ingestor class.

        :param fio: File object to run detection.
        :type fio: :py:class:`io.FileIO`
        :return: Detected ingestor class and file mime type.
        :rtype: tuple
        """
        mime_type = magic.from_buffer(fio.read(blocksize), mime=True)
        fio.seek(0)

        for ingestor_class in cls.find_ingestors():

            if mime_type in ingestor_class.MIME_TYPES:
                return ingestor_class, mime_type

        logging.getLogger(__package__).error(
            'No ingestors matched mime type: {}'.format(mime_type))

        return None, mime_type
