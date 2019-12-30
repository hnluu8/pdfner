from pdfner.document import NerDocument
from pdfner.config import IocContainer


config = {
    'search': {
        'host': 'localhost',
        'port': 4578
    },
    'nlp': {
        'spacy': {
            'include_types': None,
            'exclude_types': None
        },
        'corenlp': {
            'server': {
                'home': '/Users/h4l3/development/github/pdfner/tools/stanford-corenlp-full-2018-10-05'
            }
        }
    }
}

container = IocContainer(
    config=config
)


def index_document(filename: str, create_thumbnail: bool=False) -> NerDocument:
    pass