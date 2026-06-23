from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            pages.append(f"\n\n--- Page {page_number} ---\n{page_text}")

    return "\n".join(pages)