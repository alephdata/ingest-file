import logging
import icalendar
from vobject.base import ParseError
from banal import ensure_list
from followthemoney import model
from followthemoney.util import sanitize_text

from ingestors.ingestor import Ingestor
from ingestors.support.encoding import EncodingSupport
from ingestors.support.email import EmailIdentity
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


def cal_date(value):
    if value is None:
        return
    if hasattr(value, "dt"):
        return value.dt
    return str(value)


class CalendarIngestor(Ingestor, EncodingSupport):
    MIME_TYPES = ["text/calendar"]
    EXTENSIONS = ["ics", "ical", "icalendar", "ifb"]
    SCORE = 10

    def address_entity(self, address):
        email = str(address).strip()
        if email.lower().startswith("mailto:"):
            email = address[len("mailto:") :]
        identity = EmailIdentity(self.manager, None, email)
        return identity.entity

    def ingest_component(self, entity, idx, comp):
        if comp.name == "VCALENDAR":
            entity.add("generator", comp.get("PRODID"))
        if comp.name == "VEVENT":
            event = self.manager.make_entity("Event")
            self.manager.apply_context(event, entity)
            uid = sanitize_text(comp.get("UID"))
            if uid is not None:
                event.make_id(uid)
            else:
                event.make_id(entity.id, idx)
            event.add("proof", entity)
            event.add("name", comp.get("SUMMARY"))
            event.add("description", comp.get("DESCRIPTION"))
            event.add("location", comp.get("LOCATION"))
            event.add("sourceUrl", comp.get("URL"))
            event.add("startDate", cal_date(comp.get("DTSTART")))
            event.add("endDate", cal_date(comp.get("DTEND")))
            event.add("date", cal_date(comp.get("CREATED")))
            event.add("modifiedAt", cal_date(comp.get("LAST-MODIFIED")))
            event.add("organizer", self.address_entity(comp.get("ORGANIZER")))
            for attendee in ensure_list(comp.get("ATTENDEE")):
                event.add("involved", self.address_entity(attendee))
            self.manager.emit_entity(event, fragment=idx)

    def ingest(self, file_path, entity):
        entity.schema = model.get("PlainText")
        entity.add("encoding", "utf-8")
        text = self.read_file_decoded(entity, file_path)
        entity.set("bodyText", text)
        try:
            calendar = icalendar.Calendar.from_ical(text)
            for idx, comp in enumerate(calendar.walk()):
                self.ingest_component(entity, idx, comp)
        except Exception as exc:
            raise ProcessingException("Failed to parse iCalendar") from exc
