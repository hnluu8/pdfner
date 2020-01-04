from datetime import datetime
from elasticsearch_dsl import Document, Text, Binary, Keyword, Date, Completion, Integer


class NerDocument(Document):
    title = Text()
    document_name = Text()
    document_name_suggest = Completion()
    entities = Text()
    processed_location = Text()
    original_location = Text()
    redacted_location = Text()
    thumbnail_location = Text()
    content = Text()
    page_number = Integer()
    index_date = Date(default_timezone='UTC')

    class Index:
        name = 'pdfner'
        settings = {
            'number_of_shards': 2
        }

    def save(self, **kwargs):
        self.index_date = datetime.utcnow()
        return super().save(**kwargs)

