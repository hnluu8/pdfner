# pdfner
Information extraction and named entity recognition for indexing PDFs

## Install NLP tools
1. Download language-specific model data in spaCy
    ```
        $ python -m spacy download en
    ```
2. Download Stanford CoreNLP from https://stanfordnlp.github.io/CoreNLP/download.html and extract to {project root}/pdfner/tests/tools


## Install OCRmyPDF
https://ocrmypdf.readthedocs.io/en/latest/installation.html

## Installation
```commandline
pip install pdfner
```

## Usage
### Processing a PDF
```python
from typing import List
from pdfner import *

# Each page of the PDF is processed to an NerDocument.
processed_pdf: List[NerDocument] = process_pdf('scanned.pdf', entities_detector=SpacyDetectEntities())
print(f"Extracted text: {processed_pdf[0].text}")
print(f"Detected entities: {processed_pdf[0].entities}") 
```

### Indexing with Elasticsearch
```python
import simplejson as json
from elasticsearch import Elasticsearch
es = Elasticsearch()

# NerDocument implements for_json function for easy serialization with simplejson.
doc: NerDocument
for doc in processed_pdf:
    res = es.index(index='pdfner', id=doc.id, body=json.dumps(doc, for_json=True))
    print(res['result'])
```

### Indexing with Solr
```python
import pysolr
# Collection "gettingstarted" auto created by: solr -c -e schemaless
solr = pysolr.Solr('http://localhost:8983/solr/gettingstarted', always_commit=True)

# encode returns NerDocument object as dict which is required by pysolr 
solr.add([doc.encode() for doc in processed_pdf])
```

### API

#### process_pdf
A function that converts a scanned PDF to a text-based PDF and applies the NER detector object to the text to extract entities. Returns a list of NerDocument objects.

- **filepath: str** - path to PDF file
- **make_thumbnail: Optional[bool]=False** - whether to create a thumbnail PNG for the first page
- **cache_entities: Optional[bool]=False** - whether to cache entities to the local filesystem
- **parallelize_pages: Optional[bool]=True** - whether to process multiple pages in parallel
- **out_filepath: Optional[str]=None** - optional location of resulting processed PDF
- **entities_detector: AbstractDetectEntities** - named argument for NER detector object (SpacyDetectEntities, CoreNlpDetectEntities)
- **\*\*kwargs** - additional named arguments to attach to the returned NerDocument objects

#### AbstractDetectEntities
Roll your own NER detector by subclassing AbstractDetectEntities and overriding detect_entities.

- **detect_entities(text: str, \*\*kwargs)** - extract entities from input text and returns a list of NamedEntity objects

#### NerDocument
A class representing a single page of a processed PDF.

##### Attributes
- **id: str** - auto-generated random UUID 
- **text: str** - text extracted from PDF page
- **page_number: int** - PDF page number
- **entities: List[str]** - entities extracted from PDF text
- **processed_location: str** - location of processed PDF
- **original_location: str** - location of original PDF
- **redacted_location: str** - location of redacted PDF
- **thumbnail_location: str** - location of thumbnail PNG for first page of processed PDF
- **\*\*kwargs** - additional named arguments to store with object

##### Instance methods
- **encode()** - returns dict representation of object
- **for_json()** - for simplejson to serialize object to JSON

##### Class methods
- **decode(d: Dict)** - object_hook function for simplejson's loads function to deserialize JSON to a proper NerDocument object
