import simplejson as json
from typing import List

from pdfner import *


class TestApi:
    @classmethod
    def setup_class(cls):
        cls.processed_pdf: List[NerDocument] = None

    def test_process_pdf_spacy_entities(self, pdf_file):
        TestApi.processed_pdf = process_pdf(pdf_file, entities_detector=SpacyDetectEntities())

    def test_index_with_elasticsearch(self):
        from elasticsearch import Elasticsearch
        es = Elasticsearch()

        doc: NerDocument
        for doc in TestApi.processed_pdf:
            res = es.index(index='pdfner', id=doc.id, body=json.dumps(doc, for_json=True))
            print(res['result'])

        res = es.get(index='pdfner', id=TestApi.processed_pdf[0].id)
        # _source is a dict
        json_str = json.dumps(res['_source'])
        print(json_str)
        first = json.loads(json_str, object_hook=NerDocument.decode)
        assert first == TestApi.processed_pdf[0]

        es.indices.refresh(index='pdfner')
        res = es.search(index='pdfner', body={"query": {"match": {"entities": "ETS"}}})
        print(f"Got {res['hits']['total']['value']} hits!")

    def test_index_with_solr(self):
        import pysolr
        # Collection "gettingstarted" auto created by: solr -c -e schemaless
        solr = pysolr.Solr('http://localhost:8983/solr/gettingstarted', always_commit=True)

        solr.add([doc.encode() for doc in TestApi.processed_pdf])

        results = solr.search('entities:"ETS"')
        print(f"Saw {len(results)} results.")

