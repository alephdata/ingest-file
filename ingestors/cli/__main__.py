import sys
import logging

from ingestors.cli import cli


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')

    if sys.argv[1:]:
        cli(''.join(sys.argv[1:]))
    else:
        print('No file provided.')
        sys.exit(1)
