|pypi| |actions| |uv| |ruff| |codecov| |downloads| |clinicedc|

download-gmail-pdf
==================

Download PDF attachments from one or more Gmail accounts via IMAP.

Setup
-----

Reads account credentials from a JSON file. Set the path via the `GMAIL_ACCOUNTS_FILE`
env var or the `--accounts-file` argument.

Accounts file format (e.g. `.gmail_accounts.json`):

.. code-block:: bash

    [
        {"email": "account1@gmail.com", "password": "xxxx xxxx xxxx xxxx"},
        {"email": "account2@gmail.com", "password": "yyyy yyyy yyyy yyyy"}
    ]

Usage
-----

.. code-block:: bash

    export GMAIL_ACCOUNTS_FILE=/path/to/accounts.json

Run for all email accounts in the JSON

.. code-block:: bash

    uv run --dev download-gmail-pdfs \
      --output-dir /path/to/pdf_downloads \
      --accounts-file ~/.clinicedc/my_edc/.gmail_accounts.json

Run for one email account in the JSON

.. code-block:: bash

    uv run --dev download-gmail-pdfs \
      --email account1@gmail.com \
      --output-dir /path/to/pdf_downloads \
      --accounts-file ~/.clinicedc/my_edc/.gmail_accounts.json

Features
--------

- Tracks downloads in a manifest file (safe to re-run / resume).
- Reconnects automatically on transient network errors (up to 3 retries).

After running this, see the management command `import_labs` in clinicedc.


.. |pypi| image:: https://img.shields.io/pypi/v/download-gmail-pdfs.svg
    :target: https://pypi.python.org/pypi/download-gmail-pdfs

.. |actions| image:: https://github.com/erikvw/download-gmail-pdfs/actions/workflows/build.yml/badge.svg
  :target: https://github.com/erikvw/download-gmail-pdfs/actions/workflows/build.yml

.. |codecov| image:: https://codecov.io/gh/erikvw/download-gmail-pdfs/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/erikvw/download-gmail-pdfs

.. |downloads| image:: https://pepy.tech/badge/download-gmail-pdfs
   :target: https://pepy.tech/project/download-gmail-pdfs

.. |clinicedc| image:: https://img.shields.io/badge/framework-Clinic_EDC-green
   :alt:Made with clinicedc
   :target: https://github.com/clinicedc

.. |uv| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json
  :target: https://github.com/astral-sh/uv

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff
