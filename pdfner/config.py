import dependency_injector.containers as containers
import dependency_injector.providers as providers
from pdfner.search import ElasticsearchClient
from pdfner.document import NerDocument
from pdfner.nlp.api import *


class IocContainer(containers.DeclarativeContainer):
    """Application IoC Container """

    config = providers.Configuration('config')

    elasticsearch_client = providers.Singleton(
        ElasticsearchClient,
        host=config.search.host,
        port=config.search.port,
        document_classes=[NerDocument]
    )

    spacy_detect_entities = providers.Singleton(
        SpacyDetectEntities,
        include_types=config.nlp.spacy.include_types,
        exclude_types=config.nlp.spacy.exclude_types
    )

    corenlp_detect_entities = providers.Singleton(
        CoreNlpDetectEntities,
        core_nlp_server_home=config.nlp.corenlp.server.home
    )

