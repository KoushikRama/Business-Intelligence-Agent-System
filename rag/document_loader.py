from pathlib import Path
from docx import Document


def extract_text_from_docx(file_path: Path) -> str:
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


def load_documents(folder_path: str) -> list[dict]:
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    documents = []

    for file_path in folder.glob("*.docx"):
        content = extract_text_from_docx(file_path)

        documents.append({
            "filename": file_path.name,
            "source_path": str(file_path),
            "content": content
        })

    return documents