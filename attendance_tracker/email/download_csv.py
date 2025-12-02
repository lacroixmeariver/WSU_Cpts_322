"""Email detection and csv retrieval."""

from __future__ import annotations

import csv
import os
import pathlib
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from imap_tools import (
    AND,  # pyright: ignore[reportPrivateImportUsage] this is a spurious error, still gets the subpackages
)
from imap_tools import (
    MailBox,  # pyright: ignore[reportPrivateImportUsage] this is a spurious error, still gets the subpackages
)

import attendance_tracker.email.cleaner as cleaner
import attendance_tracker.types.tables as tables


def configure():
    """Set up the dotenv via load_dotenv."""
    load_dotenv()


def _check_processed(db_path: Path, uid) -> bool:
    with sqlite3.connect(db_path) as conn:
        # search db for uid and return if exists
        result = conn.execute("SELECT email_id FROM email_log WHERE email_id = ?", (uid,))
        return result.fetchone() is not None


def _add_to_uid_db(db_path: Path, uid) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO email_log (email_id) VALUES (?)", (uid,))


def _load_from_email(db_path: Path) -> None:
    """Check the email and download csvs in raw format."""
    configure()
    mail_password = os.getenv("mail_password")
    mail_username = os.getenv("mail_username")
    mail_server = os.getenv("mail_server")

    if not mail_password or not mail_username or not mail_server:
        raise ValueError("Missing email credentials, add to .env file")

    downloads_dir = str(Path("./docs").resolve())
    download_folder = os.path.join(downloads_dir, "downloaded_csvs")

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        print(f"Created csv download folder at {download_folder}")

    with MailBox(mail_server).login(mail_username, mail_password, "INBOX") as mailbox:
        print("Logged in successfully")
        for msg in mailbox.fetch(AND(subject="WSU Track")):
            print("\n---LOADING NEW EMAIL---")
            print(f"From: {msg.from_}")
            print(f"Subject: {msg.subject}")
            print(f"Date: {msg.date}")
            print(f"Body: {msg.text}")

            # skip adding to db if already added
            if _check_processed(db_path, msg.uid):
                print("Email Already Processed, skipping...")
                continue

            for att in msg.attachments:
                print(f"Attachment: {att.filename} ({len(att.payload)} bytes)")
                if att.filename.lower().endswith(".csv"):
                    # add to uid tracker
                    _add_to_uid_db(db_path, msg.uid)
                    print(f"Logged email UID {msg.uid} in email_log table")

                    filepath = os.path.join(download_folder, att.filename)
                    with open(filepath, "wb") as f:
                        f.write(att.payload)
                    print(f"Saved attachment to {filepath}")

                    # clean the downloaded csv
                    cleaner.clean_csv(filepath)

                    # load cleaned csv into the database
                    clean_data = pathlib.Path(
                        "./docs/downloaded_csvs/cleaned_VCEA Clubs Access Summary by Location.csv"
                    )
                    with (
                        sqlite3.connect(db_path, detect_types=sqlite3.PARSE_COLNAMES) as conn,
                        clean_data.open("r", encoding="utf-8") as more_input,
                    ):
                        inputs: list[tables.InputData] = []
                        reader = csv.reader(more_input)
                        next(reader)
                        for line in reader:
                            inputs.append(tables.InputData.from_list(line))

                        conn.executemany(inputs[0].insert_format(), inputs)
                        insert_query = f"SELECT COUNT(*) FROM {inputs[0].TABLE_NAME}"
                        count = conn.execute(insert_query).fetchone()
                        # print first column which is count
                        print(f"successfully inserted {count[0]} rows")
