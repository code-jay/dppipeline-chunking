# Mini Enterprise Knowledge Repository

This project demonstrates a small enterprise knowledge repository with documents grouped by department and a scanner script that generates a document inventory.

## Folder Structure

```text
enterprise-data/
├── hr/
│   ├── leave_policy.pdf
│   ├── handbook.pdf
├── finance/
│   ├── expense_policy.pdf
├── engineering/
│   ├── coding_guidelines.pdf
├── support/
│   ├── faq.docx
└── metadata.json
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python scan_documents.py
```

## Output

The script prints a table with:

- Document Name
- Type
- Size
- Pages
- Department
- Created Date
- Modified Date

It also creates:

```text
document_inventory.json
```
