from pdfner.document import NerDocument
from pdfner.config import IocContainer, ElasticsearchClient

container = IocContainer(
    config={
        'search': {
            'host': 'localhost',
            'port': 4571
        }
    }
)


class TestSearch:
    def test_index(self):
        doc = NerDocument(title='Hello, World!')
        es_client: ElasticsearchClient = container.elasticsearch_client()
        es_client.index(doc)

    def test_search(self):
        es_client: ElasticsearchClient = container.elasticsearch_client()
        s = NerDocument.search(using=es_client.es)
        s = s.query('match', title='World')
        result = s.execute()
        print(result)