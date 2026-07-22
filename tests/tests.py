from __future__ import annotations

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from pathlib import Path

import pytest

import download_gmail_pdfs.utils.fetch as fetch_attachments_module
from download_gmail_pdfs.utils import fetch_attachments, load_manifest, make_manifest_key


def build_message(message_id: str, attachments: list[tuple[str, bytes]]) -> bytes:
    msg = MIMEMultipart()
    msg["Message-ID"] = message_id
    msg["Subject"] = "Lab results"
    msg["Date"] = "Wed, 22 Jul 2026 10:00:00 +0000"
    for filename, content in attachments:
        part = MIMEApplication(content, _subtype="pdf")
        part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(part)
    return msg.as_bytes()


class FakeMail:
    """Stands in for imaplib.IMAP4_SSL, serving one canned message."""

    def __init__(self, raw_message: bytes, msg_num: bytes = b"1"):
        self.raw_message = raw_message
        self.msg_num = msg_num

    def search(self, *_args, **_kwargs):
        return "OK", [self.msg_num]

    def fetch(self, *_args, **_kwargs):
        return "OK", [(b"1 (BODY[])", self.raw_message)]

    def logout(self):
        pass


@pytest.fixture
def duplicate_filename_message() -> bytes:
    return build_message(
        "<msg-1>",
        [("report.pdf", b"first pdf bytes"), ("report.pdf", b"second pdf bytes")],
    )


class TestMakeManifestKey:
    def test_first_occurrence_uses_plain_key(self):
        key = make_manifest_key("<msg-1>", "report.pdf")
        assert key == "<msg-1>|report.pdf"

    def test_first_occurrence_explicit_zero_matches_default(self):
        assert make_manifest_key("<msg-1>", "report.pdf", 0) == make_manifest_key(
            "<msg-1>", "report.pdf"
        )

    def test_second_occurrence_gets_suffix(self):
        key = make_manifest_key("<msg-1>", "report.pdf", 1)
        assert key == "<msg-1>|report.pdf#1"

    def test_different_messages_same_filename_differ(self):
        key_a = make_manifest_key("<msg-1>", "report.pdf")
        key_b = make_manifest_key("<msg-2>", "report.pdf")
        assert key_a != key_b


class TestDuplicateFilenamesWithinMessage:
    """Two same-named attachments in one email must both be saved and tracked."""

    def test_both_attachments_saved_with_distinct_manifest_keys(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        duplicate_filename_message: bytes,
    ):
        monkeypatch.setattr(
            fetch_attachments_module,
            "connect",
            lambda *_a, **_kw: FakeMail(duplicate_filename_message),
        )

        saved = fetch_attachments("a@example.com", "pw", tmp_path)

        assert saved == 2
        pdf_files = sorted(p.name for p in tmp_path.glob("*.pdf"))
        assert pdf_files == ["report.pdf", "report_1.pdf"]

        manifest = load_manifest(tmp_path)
        assert "<msg-1>|report.pdf" in manifest
        assert "<msg-1>|report.pdf#1" in manifest
        assert manifest["<msg-1>|report.pdf"]["saved_as"] == "report.pdf"
        assert manifest["<msg-1>|report.pdf#1"]["saved_as"] == "report_1.pdf"

    def test_rerun_skips_both_previously_saved_duplicates(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        duplicate_filename_message: bytes,
    ):
        monkeypatch.setattr(
            fetch_attachments_module,
            "connect",
            lambda *_a, **_kw: FakeMail(duplicate_filename_message),
        )
        fetch_attachments("a@example.com", "pw", tmp_path)

        saved_again = fetch_attachments("a@example.com", "pw", tmp_path)

        assert saved_again == 0
        pdf_files = sorted(p.name for p in tmp_path.glob("*.pdf"))
        assert pdf_files == ["report.pdf", "report_1.pdf"]
