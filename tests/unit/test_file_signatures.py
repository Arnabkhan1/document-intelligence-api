from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from dia.utils.file_signatures import validate_file_signature


def create_docx_content():
    buffer = BytesIO()

    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types></Types>")
        archive.writestr("word/document.xml", "<document></document>")

    return buffer.getvalue()


# PDF tests


def test_valid_pdf_signature():
    content = b"%PDF-1.7 sample PDF content"

    assert validate_file_signature("report.pdf", content) is True


def test_invalid_pdf_signature():
    content = b"This is not a PDF"

    assert validate_file_signature("report.pdf", content) is False


# DOCX tests


def test_valid_docx_signature():
    content = create_docx_content()

    assert validate_file_signature("report.docx", content) is True


def test_invalid_docx_signature():
    content = b"This is not a DOCX"

    assert validate_file_signature("report.docx", content) is False


def test_zip_without_docx_structure():
    buffer = BytesIO()

    with ZipFile(buffer, "w") as archive:
        archive.writestr("example.txt", "Not a DOCX")

    assert validate_file_signature("report.docx", buffer.getvalue()) is False


# TXT tests


def test_valid_txt_content():
    content = b"Hello Document Intelligence API"

    assert validate_file_signature("report.txt", content) is True


def test_invalid_txt_content():
    content = b"\xff\xfe\xfa"

    assert validate_file_signature("report.txt", content) is False


# Unsupported extension test


def test_unsupported_file_extension():
    content = b"some content"

    assert validate_file_signature("report.exe", content) is False
