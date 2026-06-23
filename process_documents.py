from pathlib import Path
from datetime import datetime
import json
import re

from pypdf import PdfReader
from docx import Document


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "enterprise-data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CHUNKS_FILE = OUTPUT_DIR / "processed_chunks.json"


SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"]


def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)

    return "\n".join(text)


def extract_text_from_docx(file_path: Path) -> str:
    doc = Document(str(file_path))
    paragraphs = []

    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text.strip())

    return "\n".join(paragraphs)


def extract_text_from_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def extract_text(file_path: Path) -> str:
    if file_path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(file_path)

    if file_path.suffix.lower() == ".docx":
        return extract_text_from_docx(file_path)

    if file_path.suffix.lower() == ".txt":
        return extract_text_from_txt(file_path)

    return ""


def clean_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def get_department(file_path: Path) -> str:
    relative_path = file_path.relative_to(DATA_DIR)
    return relative_path.parts[0]


def process_documents():
    OUTPUT_DIR.mkdir(exist_ok=True)

    all_chunks = []

    for file_path in DATA_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.name == "metadata.json":
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        print(f"Processing: {file_path.name}")

        raw_text = extract_text(file_path)
        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text)

        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "document_name": file_path.name,
                "department": get_department(file_path),
                "file_type": file_path.suffix.lower(),
                "chunk_index": index,
                "chunk_text": chunk,
                "chunk_length": len(chunk),
                "source_path": str(file_path.relative_to(PROJECT_ROOT)),
                "processed_at": datetime.now().isoformat()
            })

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print("\nDocument processing completed.")
    print(f"Total chunks created: {len(all_chunks)}")
    print(f"Output saved to: {CHUNKS_FILE}")


if __name__ == "__main__":
    process_documents()