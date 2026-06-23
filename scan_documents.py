from __future__ import annotations

import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "enterprise-data"
OUTPUT_DIR = PROJECT_ROOT / "output"
METADATA_FILE = DATA_DIR / "metadata.json"

BASE_DIR = DATA_DIR
OUTPUT_JSON = OUTPUT_DIR / "document_inventory.json"
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".html", ".htm"]

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def format_date(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def get_pdf_pages(file_path: Path) -> int | str:
    if PdfReader is None:
        return "Install pypdf"
    try:
        reader = PdfReader(str(file_path))
        return len(reader.pages)
    except Exception as exc:
        return f"Error: {exc}"


def get_docx_pages(file_path: Path) -> int | str:
    """
    DOCX does not store a reliable page count by default.
    This function first tries LibreOffice conversion to PDF and counts PDF pages.
    If LibreOffice is unavailable, it returns paragraph count as a fallback note.
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    "soffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    tmpdir,
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            converted_pdf = Path(tmpdir) / f"{file_path.stem}.pdf"
            if result.returncode == 0 and converted_pdf.exists():
                return get_pdf_pages(converted_pdf)
    except Exception:
        pass

    if Document is None:
        return "Install python-docx"

    try:
        doc = Document(str(file_path))
        return f"N/A ({len(doc.paragraphs)} paragraphs)"
    except Exception as exc:
        return f"Error: {exc}"


def get_pages(file_path: Path) -> int | str:
    if file_path.suffix.lower() == ".pdf":
        return get_pdf_pages(file_path)
    if file_path.suffix.lower() == ".docx":
        return get_docx_pages(file_path)
    return "N/A"


def scan_documents() -> list[dict[str, Any]]:
    inventory = []

    for file_path in sorted(BASE_DIR.rglob("*")):
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            continue

        stat = file_path.stat()
        department = file_path.parent.name

        inventory.append(
            {
                "document_name": file_path.name,
                "type": extension.replace(".", "").upper(),
                "size": format_size(stat.st_size),
                "size_bytes": stat.st_size,
                "pages": get_pages(file_path),
                "department": department,
                "created_date": format_date(stat.st_ctime),
                "modified_date": format_date(stat.st_mtime),
                "relative_path": str(file_path.relative_to(BASE_DIR.parent)),
            }
        )

    return inventory


def print_table(rows: list[dict[str, Any]]) -> None:
    headers = [
        "Document Name",
        "Type",
        "Size",
        "Pages",
        "Department",
        "Created Date",
        "Modified Date",
    ]

    table_rows = [
        [
            row["document_name"],
            row["type"],
            row["size"],
            str(row["pages"]),
            row["department"],
            row["created_date"],
            row["modified_date"],
        ]
        for row in rows
    ]

    widths = [len(header) for header in headers]
    for row in table_rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(value))

    def line(values: list[str]) -> str:
        return " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(values))

    print(line(headers))
    print("-+-".join("-" * width for width in widths))
    for row in table_rows:
        print(line(row))


def main() -> None:
    if not BASE_DIR.exists():
        raise FileNotFoundError(f"Folder not found: {BASE_DIR}")

    inventory = scan_documents()
    print_table(inventory)

    OUTPUT_JSON.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    print(f"\nInventory saved to: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
