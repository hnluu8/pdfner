from typing import List, Type
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch_dsl import Document


class ElasticsearchClient(object):
    def __init__(self, host: str, port: int, document_classes: List[Type[Document]]):
        if host == 'localhost' or host == '127.0.0.1':
            self.es = Elasticsearch(hosts=[{'host': host, 'port': port}])
        else:
            from botocore.session import get_session
            from requests_aws4auth import AWS4Auth

            session = get_session()
            awsauth = AWS4Auth(session.get_credentials().access_key,
                               session.get_credentials().secret_key,
                               session.get_config_variable('region'),
                               'es')
            self.es = Elasticsearch(
                hosts=[{'host': host, 'port': port}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection
            )

        # TODO: if using a pipeline to pre-process documents before they're indexed, the pipeline _must_ be created
        # before the index, which will normally be triggered when Document class method init() is called.
        for cls in document_classes:
            cls.init(using=self.es)

    def index(self, document: Document, **kwargs):
        return document.save(using=self.es, **kwargs)


