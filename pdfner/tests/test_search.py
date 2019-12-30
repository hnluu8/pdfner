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
        doc = NerDocument(title='A document to test with',
                          document_name='test')
        es_client: ElasticsearchClient = container.elasticsearch_client()
        es_client.index(doc)

    def test_search_by_single_field(self):
        es_client: ElasticsearchClient = container.elasticsearch_client()
        s = NerDocument.search(using=es_client.es)
        s = s.query('match', title='test')
        result = s.execute()
        print(result)

    def test_search_by_multiple_fields(self):
        es_client: ElasticsearchClient = container.elasticsearch_client()
        s = NerDocument.search(using=es_client.es)
        s = s.highlight_options(order='score')
        s = s.highlight('title')
        s = s.highlight('document_name')
        s = s.query('multi_match', query='test', fields=['document_name', 'title'], type='best_fields')
        result = s.execute()
        print(result)