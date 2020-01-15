import os
import simplejson as json # Prefer simplejson for proper namedtuple serde
from collections import namedtuple
from dask import delayed, compute
from typing import List, Optional

from pdfner.pdf import PdfUtils
from pdfner.nlp import AbstractDetectEntities
from pdfner.document import NerDocument


def process_pdf(filepath: str,
                make_thumbnail: Optional[bool]=False,
                cache_entities: Optional[bool]=False,
                parallelize_pages: Optional[bool]=True,
                out_filepath: Optional[str]=None,
                *,
                entities_detector: AbstractDetectEntities,
                **kwargs) -> List[NerDocument]:
    processed_filepath, thumbnail_filepath = PdfUtils.convert_scanned_document(filepath, result_text_pdf_file=out_filepath, make_thumbnail=make_thumbnail)

    process_pages = []
    entities_file = None
    root, ext = os.path.splitext(filepath)
    text_pages = PdfUtils.get_text_pages(processed_filepath)
    for i, text in enumerate(text_pages):
        page_number = i + 1
        if cache_entities:
            entities_file = root + f" (page {page_number}).json"
        process_page = delayed(_process_page)(text, page_number, processed_filepath, filepath, thumbnail_filepath, entities_file, entities_detector, **kwargs)
        process_pages.append(process_page)

    results = compute(*process_pages, scheduler='processes' if parallelize_pages else 'single-threaded')
    return results


def _process_page(text: str,
                  page_number: int,
                  processed_location: str,
                  original_location: str,
                  thumbnail_location: str,
                  entities_file: str,
                  entities_detector: AbstractDetectEntities,
                  **kwargs) -> NerDocument:
    if entities_file is not None:
        if not os.path.exists(entities_file):
            entities = entities_detector.detect_entities(text)
            entities_json = json.dumps(entities)
            with open(entities_file, 'w') as f:
                f.write(entities_json)
        else:
            entities = []
            with open(entities_file) as f:
                entities_list = json.load(f)
                for d in entities_list:
                    entities.append(namedtuple('NamedEntity', d.keys())(**d))
    else:
        entities = entities_detector.detect_entities(text)
    final_entities = list(set(x.text for x in entities if len(x.text) > 2))
    return NerDocument(text=text,
                       page_number=page_number,
                       entities=final_entities,
                       processed_location=processed_location,
                       original_location=original_location,
                       thumbnail_location=thumbnail_location,
                       **kwargs)
