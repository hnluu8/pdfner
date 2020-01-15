import textacy
import textacy.extract
from typing import List, Optional
from pdfner.nlp.base import AbstractDetectEntities, NamedEntity


class SpacyDetectEntities(AbstractDetectEntities):
    def __init__(self,  include_types: Optional[List[str]]=None, exclude_types: Optional[List[str]]=None, lang: Optional[str]='en'):
        self.include_types = include_types
        self.exclude_types = exclude_types
        self.lang = lang

    def detect_entities(self, text: str, **kwargs) -> List[NamedEntity]:
        # python -m spacy download en
        doc = textacy.Doc(textacy.preprocess_text(text, **kwargs), lang=self.lang)
        entities = list(textacy.extract.named_entities(doc, drop_determiners=True, include_types=self.include_types, exclude_types=self.exclude_types))
        nes = [NamedEntity(ne.label_, ne.text) for ne in entities]
        return nes
