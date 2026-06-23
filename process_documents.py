from pathlib import Path
from datetime import datetime
import json
import re

from processors.pdf_processor import extract_text_from_pdf
from processors.docx_processor import extract_text_from_docx
from processors.txt_processor import extract_text_from_txt
from processors.html_processor import extract_text_from_html
from chunking_strategies import chunk_document


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "enterprise-data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CHUNKS_FILE = OUTPUT_DIR / "processed_chunks.json"

SUPPORTED_EXTENSIONS = [
    ".pdf", ".docx", ".txt", ".html", ".htm",
    ".csv", ".xlsx",
    ".py", ".js", ".java", ".php", ".ts"
]

def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    if suffix == ".docx":
        return extract_text_from_docx(file_path)
    if suffix == ".txt":
        return extract_text_from_txt(file_path)
    if suffix in [".html", ".htm"]:
        return extract_text_from_html(file_path)

    return ""


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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

        if not cleaned_text:
            print(f"Skipping empty document: {file_path.name}")
            continue

        metadata = {
            "document_id": file_path.stem,
            "document_name": file_path.name,
            "department": get_department(file_path),
            "file_type": file_path.suffix.lower().replace(".", ""),
            "source_path": str(file_path.relative_to(PROJECT_ROOT)),
            "processed_at": datetime.now().isoformat()
        }

        document = {
            "text": cleaned_text,
            "metadata": metadata
        }

        chunks = chunk_document(document)

        for chunk in chunks:
            all_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "document_name": metadata["document_name"],
                "department": metadata["department"],
                "file_type": metadata["file_type"],
                "chunk_index": chunk["chunk_index"],
                "chunk_text": chunk["text"],
                "chunk_length": len(chunk["text"]),
                "chunking_strategy": chunk["chunking_strategy"],
                "source_path": metadata["source_path"],
                "processed_at": metadata["processed_at"]
            })

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print("\nDocument processing completed.")
    print(f"Total chunks created: {len(all_chunks)}")
    print(f"Output saved to: {CHUNKS_FILE}")


if __name__ == "__main__":
    process_documents()