from ingestors.log import get_logger
from banal import ensure_list
from countrytagger import tag_place


log = get_logger(__name__)


def location_country(location):
    code, score, country = tag_place(location)
    return ensure_list(country)
