from pathlib import Path
from docx import Document


def extract_text_from_docx(file_path: Path) -> str:
    doc = Document(str(file_path))
    paragraphs = []

    for para in doc.paragraphs:
        text = para.text.strip()

        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)