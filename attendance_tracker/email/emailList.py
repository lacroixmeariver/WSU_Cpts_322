"""sends emails to admins and handles admin management."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from smtplib import SMTP

from dotenv import load_dotenv


def configure():
    """Set up the dotenv via load_dotenv."""
    load_dotenv()


def add_admin_email(db_path: Path, email: str) -> None:
    """Add an admin email to the admin_emails table."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO admin_emails (admin_email) VALUES (?)",
            (email,),
        )
    print(f"Added admin email: {email}")


def remove_admin_email(db_path: Path, email: str) -> None:
    """Remove an admin email from the admin_emails table."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "DELETE FROM admin_emails WHERE admin_email = ?",
            (email,),
        )
    print(f"Removed admin email: {email}")


def get_admin_emails(db_path: Path) -> list[str]:
    """Retrieve all admin emails from the admin_emails table."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT admin_email FROM admin_emails")
        emails = [row[0] for row in cursor.fetchall()]

    return emails


def send_email_to_admins(db_path: Path, email_content: MIMEMultipart) -> None:
    """Send an email to all admin emails."""
    configure()
    mail_password = os.getenv("mail_password")
    mail_sender = os.getenv("mail_username")

    receiver_emails = get_admin_emails(db_path)
    compound_receiver = ""
    print(f"Sending email to admins: {receiver_emails}")
    for receiver in receiver_emails:
        compound_receiver += receiver + ", "

    if not mail_password or not mail_sender:
        raise ValueError("Missing email credentials, add to .env file")
    email_content["To"] = compound_receiver
    email_content["From"] = mail_sender
    with SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(mail_sender, mail_password)
        smtp.send_message(email_content)
        print(f"Sent email to {compound_receiver}")


def send_error_email(db_path: Path) -> None:
    """Send an error email to all admin emails."""
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    subject = "Club Tracker Error Notification"
    body = f"This is an error email sent at {current_time} to verify admin email functionality."

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    send_email_to_admins(db_path, msg)


def send_report_email(db_path: Path) -> None:
    """Send a monthly report email to all admin emails."""
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    subject = "Club Tracker Monthly Report"
    body = f"This is a monthly club attendance report sent at {current_time}."

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    send_email_to_admins(db_path, msg)
