import re
from typing import List, Dict


def fixed_size_chunk(text: str, chunk_size=800, overlap=120):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def paragraph_chunk(text: str):
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if len(p.strip()) > 50]


def section_chunk(text: str):
    sections = re.split(r"\n(?=[A-Z][A-Za-z\s]{3,50}\n)", text)
    return [s.strip() for s in sections if len(s.strip()) > 100]


def code_chunk(text: str):
    pattern = r"(def\s+\w+\(.*?\):|class\s+\w+.*?:)"
    parts = re.split(pattern, text)

    chunks = []
    current = ""

    for part in parts:
        if re.match(pattern, part):
            if current.strip():
                chunks.append(current.strip())
            current = part
        else:
            current += part

    if current.strip():
        chunks.append(current.strip())

    return chunks


def table_chunk(text: str):
    lines = text.splitlines()
    chunks = []
    current = []

    for line in lines:
        if "," in line or "|" in line or "\t" in line:
            current.append(line)
        else:
            if current:
                chunks.append("\n".join(current))
                current = []

    if current:
        chunks.append("\n".join(current))

    return chunks


def choose_chunking_strategy(file_type: str, text: str):
    file_type = file_type.lower().replace(".", "")

    if file_type in ["csv", "xlsx"]:
        return "table"

    if file_type in ["py", "js", "java", "php", "ts"]:
        return "code"

    if "faq" in text.lower() or "question:" in text.lower():
        return "faq"

    if file_type in ["pdf", "docx", "html"]:
        return "section"

    return "fixed"


def chunk_document(document: Dict) -> List[Dict]:
    text = document["text"]
    metadata = document["metadata"]
    file_type = metadata.get("file_type", "txt")

    strategy = choose_chunking_strategy(file_type, text)

    if strategy == "table":
        raw_chunks = table_chunk(text)
    elif strategy == "code":
        raw_chunks = code_chunk(text)
    elif strategy == "section":
        raw_chunks = section_chunk(text)
    elif strategy == "faq":
        raw_chunks = paragraph_chunk(text)
    else:
        raw_chunks = fixed_size_chunk(text)

    if not raw_chunks:
        raw_chunks = fixed_size_chunk(text)
        strategy = "fixed"

    final_chunks = []
    final_index = 0

    for chunk in raw_chunks:
        if len(chunk) > 1200:
            smaller_chunks = fixed_size_chunk(chunk, chunk_size=800, overlap=120)
            used_strategy = f"{strategy}+fixed"
        else:
            smaller_chunks = [chunk]
            used_strategy = strategy

        for small_chunk in smaller_chunks:
            final_chunks.append({
                "chunk_id": f"{metadata.get('document_id')}_chunk_{final_index}",
                "document_id": metadata.get("document_id"),
                "text": small_chunk,
                "chunk_index": final_index,
                "chunking_strategy": used_strategy,
                "metadata": metadata
            })
            final_index += 1

    return final_chunks