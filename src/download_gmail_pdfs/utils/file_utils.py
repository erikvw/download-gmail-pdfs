from email.header import decode_header
from pathlib import Path


def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in "._- " else "_" for c in name).strip()


def decode_header_value(value: str) -> str:
    parts = decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def get_filename_from_message_part(part) -> tuple[str, str] | None:
    content_type = part.get_content_type()
    filename = part.get_filename()
    if filename:
        filename = decode_header_value(filename)

    is_pdf = content_type == "application/pdf" or (
        filename and filename.lower().endswith(".pdf")
    )
    if not is_pdf or part.get("Content-Disposition") is None:
        result = None
    else:
        original_filename = filename or "attachment.pdf"
        filename = sanitize_filename(original_filename)
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        result = filename, original_filename
    return result


def get_or_rename_path(output_dir: Path, filename: str) -> Path:
    """Rename file if a file exists with the same name."""
    path = output_dir / filename
    if path.exists():
        stem = path.stem
        suffix = path.suffix
        n = 1
        while path.exists():
            path = output_dir / f"{stem}_{n}{suffix}"
            n += 1
    return path
