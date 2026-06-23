from pathlib import Path
from bs4 import BeautifulSoup


def extract_text_from_html(file_path: Path) -> str:
    html = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return soup.get_text(separator="\n")