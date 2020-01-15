import simplejson as json
from pdfner.document import NerDocument


class TestJsonSerde:
    @classmethod
    def setup_class(cls):
        cls.document = NerDocument(text='Hello, World!',
                                   page_number=1,
                                   entities=['Hello', 'World'],
                                   processed_location='',
                                   original_location='',
                                   foo='bar')
        cls.json = None

    def test_json_serialization(self):
        TestJsonSerde.json = json.dumps(TestJsonSerde.document, for_json=True)
        print(TestJsonSerde.json)

    def test_json_deserialization(self):
        doc: NerDocument = json.loads(TestJsonSerde.json, object_hook=NerDocument.decode)
        assert doc.id() == TestJsonSerde.document.id()
