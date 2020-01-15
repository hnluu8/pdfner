import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional


class NerDocument(object):
    def __init__(self,
                 *,
                 text: str,
                 page_number: int,
                 entities: List[str],
                 processed_location: str,
                 original_location: str,
                 redacted_location: Optional[str]=None,
                 thumbnail_location: Optional[str]=None,
                 **kwargs):
        self.id = str(uuid.uuid4())
        self._processed_utc = datetime.now(timezone.utc)
        self.text = text
        self.page_number = page_number
        self.entities = entities
        self.processed_location = processed_location
        self.original_location = original_location
        self.redacted_location = redacted_location
        self.thumbnail_location = thumbnail_location
        for k, v in kwargs.items():
            setattr(self, k, v)

    def encode(self):
        d = self.__dict__.copy()
        d['_processed_utc'] = self._processed_utc.isoformat()
        return d

    # Function called by simplejson to serialize NerDocument object to JSON.
    def for_json(self):
        return self.encode()

    # object_hook function called by simplejson to deserialize JSON to NerDocument object.
    @classmethod
    def decode(cls, d: Dict):
        d['_processed_utc'] = datetime.strptime(d['_processed_utc'], '%Y-%m-%dT%H:%M:%S.%f%z')
        return cls(**d)

    def __eq__(self, other):
        if not isinstance(other, NerDocument):
            return NotImplemented

        return self.id == other.id

    def __hash__(self):
        return hash(self.id,)

