import os
import sys
import pynlp
from requests.exceptions import ConnectionError
from typing import List
from subprocess import Popen, PIPE
from pdfner.nlp.base import AbstractDetectEntities, NamedEntity


class CoreNlpDetectEntities(AbstractDetectEntities):
    def __init__(self, core_nlp_server_home: str):
        self.core_nlp_server_home = core_nlp_server_home

    def detect_entities(self, text: str, **kwargs) -> List[NamedEntity]:
        document = CoreNlpDetectEntities._try_core_nlp(text, self.core_nlp_server_home)
        nes = [NamedEntity(ne.type, str(ne)) for ne in document.entities]
        return nes

    @staticmethod
    def _try_core_nlp(text: str, core_nlp_server_home: str, annotators='ner', options={'openie.resolve_coref': True}):
        nlp = pynlp.StanfordCoreNLP(annotators=annotators, options=options)
        try:
            document = nlp(text.encode('utf-8'))
            return document
        except ConnectionError as e:
            try:
                core_nlp_env = os.environ.copy()
                core_nlp_env['CORE_NLP'] = core_nlp_server_home
                # Core NLP server will continue to run and listen on port 9000 after this script has terminated.
                Popen([sys.executable, '-m', 'pynlp'], env=core_nlp_env, stdout=PIPE)
                document = nlp(text.encode('utf-8'))
                return document
            except Exception as e:
                print('Attempted to auto launch StanfordCoreNLPServer but failed...check open ports on your machine (mac: lsof -i -P | grep -i "listen").')
                raise e
