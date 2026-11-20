from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile


def validate_file_signature(filename: str, content: bytes) -> bool:
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        return content.startswith(b"%PDF-")

    if extension == ".docx":
        try:
            with ZipFile(BytesIO(content)) as archive:
                required_files = {
                    "[Content_Types].xml",
                    "word/document.xml",
                }

                return required_files.issubset(archive.namelist())

        except BadZipFile:
            return False

    if extension == ".txt":
        try:
            content.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False

    return False
