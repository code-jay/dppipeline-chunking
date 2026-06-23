# Enterprise Knowledge Repository

A production-ready **Enterprise Document Processing Pipeline** for
building **Retrieval-Augmented Generation (RAG)** and **Enterprise AI
Knowledge Assistants**.

## Architecture

``` text
Enterprise Documents
        ↓
Document Scanner
        ↓
Metadata Extraction
        ↓
Text Extraction
        ↓
Cleaning & Normalization
        ↓
Intelligent Chunking
        ↓
processed_chunks.json
        ↓
Embeddings
        ↓
PostgreSQL + pgvector
        ↓
Semantic Retrieval
        ↓
Enterprise RAG
```

## Project Structure

``` text
Enterprise-Knowledge-Repository/
├── enterprise-data/
├── processors/
├── output/
├── scan_documents.py
├── process_documents.py
├── chunking_strategies.py
├── requirements.txt
└── README.md
```

## Features

-   PDF/DOCX/TXT/HTML processing
-   Metadata extraction
-   Intelligent chunking
-   Hybrid chunking
-   JSON output

## Chunking Strategies

-   Section Chunking
-   Paragraph Chunking
-   Table Chunking
-   Code Chunking
-   Fixed Size Chunking

## Next Phase

processed_chunks.json → Embeddings → PostgreSQL + pgvector → Semantic
Search → RAG

## Tech Stack

Python, PyPDF, python-docx, BeautifulSoup4, PostgreSQL, pgvector,
FastAPI
