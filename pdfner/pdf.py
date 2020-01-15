import os
import time
import fitz
import pikepdf
import img2pdf
from subprocess import Popen
from typing import Set
from fitz.utils import getColor
from pathlib import Path
from pdf2image import convert_from_path


class PdfUtils(object):
    @staticmethod
    def convert_scanned_document(scanned_pdf_file: str, result_text_pdf_file: str=None, make_thumbnail: bool=True, force_ocr: bool=False):
        root = None
        if result_text_pdf_file is None:
            root, ext = os.path.splitext(scanned_pdf_file)
            result_text_pdf_file = root + ' (processed).pdf'
        result_thumbnail_file = None
        if make_thumbnail:
            if not root:
                root, ext = os.path.splitext(result_text_pdf_file)
            result_thumbnail_file = root + '.png'
        mat = fitz.Matrix(0.4, 0.4)
        # Are there any pages that may already be text-based?
        non_text_page_numbers = []
        doc: fitz.Document = fitz.open(scanned_pdf_file)
        for page in doc:
            if not page.getText():
                non_text_page_numbers.append(page.number)
            if page.number == 0 and make_thumbnail:
                pix = page.getPixmap(matrix=mat, alpha=False)
                pix.writePNG(result_thumbnail_file)
        if not non_text_page_numbers:
            if force_ocr:
                print(f"\nConverting {scanned_pdf_file}...")
                # deskew crooked PDFs seems to do better with honoring whitespace, but it also failed to incorrectly identify the word "Illness" as llIness.
                # Popen(f'ocrmypdf --deskew "{scanned_pdf_file}" "{result_text_pdf_file}"', shell=True).wait()
                Popen(f'ocrmypdf --force-ocr "{scanned_pdf_file}" "{result_text_pdf_file}"', shell=True).wait()
            else:
                result_text_pdf_file = scanned_pdf_file
                print('\nDocument already has text. Nothing to do.')
        else:
            diff = set(range(len(doc))) - set(non_text_page_numbers)
            if diff:
                # Doc in memory now has only scanned pages.
                subset_pdf_file = root + ' (scanned).pdf'
                doc.select(non_text_page_numbers)
                doc.save(subset_pdf_file, garbage=4)
                print(f"\nConverting {subset_pdf_file}...")
                Popen(f'ocrmypdf "{subset_pdf_file}" "{result_text_pdf_file}"', shell=True).wait()
                # Add the text-based pages from the original doc to the result text pdf.
                original_doc: fitz.Document = fitz.open(scanned_pdf_file)
                result_doc: fitz.Document = fitz.open(result_text_pdf_file)
                print(f"\nInserting text-based pages from {scanned_pdf_file} into {result_text_pdf_file}...")
                for page_number in diff:
                    result_doc.insertPDF(original_doc, from_page=page_number, to_page=page_number, start_at=page_number)
                    result_doc.saveIncr()
                original_doc.close()
            else:
                print(f"\nConverting {scanned_pdf_file}...")
                # deskew crooked PDFs seems to do better with honoring whitespace, but it also failed to incorrectly identify the word "Illness" as llIness.
                # Popen(f'ocrmypdf --deskew "{scanned_pdf_file}" "{result_text_pdf_file}"', shell=True).wait()
                Popen(f'ocrmypdf "{scanned_pdf_file}" "{result_text_pdf_file}"', shell=True).wait()
        return result_text_pdf_file, result_thumbnail_file

    @staticmethod
    def convert_scanned_documents(scanned_pdf_dir: str, result_text_pdf_dir: str=None):
        path = Path(scanned_pdf_dir)
        for item in path.glob("*.pdf"):
            if item.is_file():
                PdfUtils.convert_scanned_document(item)

    @staticmethod
    def get_text(pdf_file):
        combined_text = ''
        start_time = time.time()
        if isinstance(pdf_file, str) or isinstance(pdf_file, Path):
            doc: fitz.Document = fitz.open(pdf_file)
        else:
            # Open Document from stream.
            stream = pdf_file.read()
            doc: fitz.Document = fitz.open('pdf', stream)

        for page in doc:
            text = page.getText()
            if not text:
                raise RuntimeError(f"Page {page.number + 1} doesn't contain any text.")
            combined_text += text
        doc.close()
        elapsed_time = time.time() - start_time
        print(f'get_text: {elapsed_time}\n')
        return combined_text

    @staticmethod
    def get_text_pages(pdf_file):
        text_pages = []
        start_time = time.time()
        if isinstance(pdf_file, str) or isinstance(pdf_file, Path):
            doc: fitz.Document = fitz.open(pdf_file)
        else:
            # Open Document from stream.
            stream = pdf_file.read()
            doc: fitz.Document = fitz.open('pdf', stream)

        for page in doc:
            text = page.getText()
            if not text:
                raise RuntimeError(f"Page {page.number + 1} doesn't contain any text.")
            text_pages.append(text)
        doc.close()
        elapsed_time = time.time() - start_time
        print(f'get_text_pages: {elapsed_time}\n')
        return text_pages

    @staticmethod
    def redact_document(pdf_file, identifiers: Set[str], redacted_pdf_file: str=None):
        root = None
        if redacted_pdf_file is None:
            root, ext = os.path.splitext(pdf_file)
            redacted_pdf_file = root + ' (redacted).pdf'
        if not root:
            root, ext = os.path.splitext(redacted_pdf_file)
        # 1. Visually redact the identifiers.
        identifiers = [id.strip().replace('\n', ' ') for id in identifiers]
        black = getColor('black')
        doc: fitz.Document = fitz.open(pdf_file)
        for page in doc:
            for id in identifiers:
                rl = page.searchFor(id)
                for rect in rl:
                    page.drawRect(rect, fill=black)
        doc.save(redacted_pdf_file)
        new_doc = pikepdf.new()
        # 2. Convert redacted pdf to images
        images = convert_from_path(redacted_pdf_file)
        for i, image in enumerate(images):
            img_file = root + f" (redacted {i + 1}).png"
            image.save(img_file, 'png', dpi=(200, 200), optimize=True)
            # image.save(img_file, 'png', optimize=True)
            img_pdf_file = root + f" (redacted {i + 1}).pdf"
            with open(img_pdf_file, 'wb') as outf:
                img2pdf.convert(img_file, layout_fun=img2pdf.default_layout_fun, with_pdfrw=False, outputstream=outf)
            img_pdf = pikepdf.open(img_pdf_file)
            new_doc.pages.extend(img_pdf.pages)
        # 3. Save images as a new scanned document.
        new_doc.save(redacted_pdf_file)
        # 4. Make the new scanned document searchable.
        PdfUtils.convert_scanned_document(redacted_pdf_file, make_thumbnail=False)