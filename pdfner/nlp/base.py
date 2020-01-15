from typing import List, NamedTuple
from abc import ABCMeta, abstractmethod


class NamedEntity(NamedTuple):
    type: str
    text: str
    category: str = None


class AbstractDetectEntities(object, metaclass=ABCMeta):
    @abstractmethod
    def detect_entities(self, text: str, **kwargs) -> List[NamedEntity]:
        pass
