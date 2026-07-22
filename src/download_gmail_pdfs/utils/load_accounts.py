import json
from pathlib import Path


def load_accounts(accounts_file: Path) -> list[dict[str, str]]:
    data = json.loads(accounts_file.read_text())
    if not isinstance(data, list) or not data:
        raise ValueError("Accounts file must be a non-empty JSON array.")
    for i, entry in enumerate(data):
        if "email" not in entry or "password" not in entry:
            raise ValueError(f"Account entry {i} missing 'email' or 'password'.")
    return data
