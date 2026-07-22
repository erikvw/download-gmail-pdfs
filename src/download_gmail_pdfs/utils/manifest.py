import json
import sys
from pathlib import Path

MANIFEST_FILENAME = ".downloaded_pdfs.json"


def save_manifest(output_dir: Path, manifest: dict) -> None:
    manifest_path = output_dir / MANIFEST_FILENAME
    manifest_path.write_text(json.dumps(manifest, indent=2))


def make_manifest_key(message_id: str, original_filename: str, occurrence: int = 0) -> str:
    """Build a manifest key, disambiguating repeated filenames within one message.

    `occurrence` is the 0-based index of this filename among attachments seen
    so far in the same message. Keeping the plain key for occurrence 0 preserves
    compatibility with manifests written before this disambiguation existed.
    """
    if occurrence == 0:
        return f"{message_id}|{original_filename}"
    return f"{message_id}|{original_filename}#{occurrence}"


def load_manifest(output_dir: Path) -> dict:
    """Load the manifest of previously downloaded attachments.

    Structure:
        {
            "<message_id>|<original_filename>": {
                "saved_as": "actual_file.pdf",
                "subject": "...",
                "date": "..."
            },
            ...
        }

    Note: if a single message has more than one attachment sharing the same
    original_filename, keys for the 2nd and later occurrences are suffixed
    with "#<n>" (see make_manifest_key) so they don't collide.
    """
    manifest = {}
    manifest_path = output_dir / MANIFEST_FILENAME
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest:
            sys.stdout.write(
                f"Manifest has {len(manifest)} previously downloaded PDF(s) — skipping.\n"
            )
    return manifest
