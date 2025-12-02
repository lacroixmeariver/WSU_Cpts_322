"""sends emails to admins and handles admin management."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from smtplib import SMTP

from dotenv import load_dotenv


def configure(db_path: Path) -> None:
    """Set up the dotenv via load_dotenv."""
    load_dotenv()
    # add permanent superadmins
    # remove and re-add to avoid duplicates
    # remove_admin_email(db_path,"gary.offerdahl@wsu.edu")
    # remove_admin_email(db_path,"maynard.siev@wsu.edu")
    # remove_admin_email(db_path,"vcea.studentclubs@wsu.edu")
    # add_admin_email(db_path,"gary.offerdahl@wsu.edu", True)
    # add_admin_email(db_path,"maynard.siev@wsu.edu", True)
    # add_admin_email(db_path,"vcea.studentclubs@wsu.edu", True)


# TODO: UNCOMMENT THE PERMANENT SUPERADMIN EMAILS BEFORE DEPLOYMENT
# TODO: COMMENTED OUT TO PREVENT SPAMMING USERS DURING TESTING

# had to add in conn as an argument instead of dbpath to be able to use it in ADMIN


def add_admin_email(conn: sqlite3.Connection, email: str, permanent: bool = False) -> None:
    """Add an admin email to the admin_emails table."""
    # permanent is only used for superadmins
    # default to False for normal admins
    try:
        with conn:
            conn.execute(
                "INSERT INTO admin_emails (admin_email, permanent) VALUES (?,?)",
                (email, permanent),
            )
        print(f"Added admin email: {email}")
    except sqlite3.IntegrityError:
        print(f"Admin email {email} already exists, not adding duplicate.")


def remove_admin_email(conn: sqlite3.Connection, email: str) -> None:
    """Remove an admin email from the admin_emails table."""
    try:
        if is_permanent_admin(conn, email):
            print(f"Admin email {email} is a permanent superadmin, cannot remove through webapp.")
            return
        with conn:
            conn.execute(
                "DELETE FROM admin_emails WHERE admin_email = ?",
                (email,),
            )
        print(f"Removed admin email: {email}")
    except sqlite3.IntegrityError:
        print(f"Admin email {email} does not exist, cannot remove.")


def is_permanent_admin(conn: sqlite3.Connection, email: str) -> bool:
    """Check if an admin email is permanent."""
    with conn:
        cursor = conn.execute(
            "SELECT permanent FROM admin_emails WHERE admin_email = ?",
            (email,),
        )
        result = cursor.fetchone()
        if result:
            return bool(result[0])
    return False


def add_admin_email_dbpath(db_path: Path, email: str, permanent: bool = False) -> None:
    """Add an admin email to the admin_emails table."""
    # permanent is only used for superadmins
    # default to False for normal admins
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "INSERT INTO admin_emails (admin_email, permanent) VALUES (?,?)",
                (email, permanent),
            )
        print(f"Added admin email: {email}")
    except sqlite3.IntegrityError:
        print(f"Admin email {email} already exists, not adding duplicate.")


def remove_admin_email_dbpath(db_path, email: str) -> None:
    """Remove an admin email from the admin_emails table."""
    try:
        if is_permanent_admin_dbpath(db_path, email):
            print(f"Admin email {email} is a permanent superadmin, cannot remove through webapp.")
            return
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "DELETE FROM admin_emails WHERE admin_email = ?",
                (email,),
            )
        print(f"Removed admin email: {email}")
    except sqlite3.IntegrityError:
        print(f"Admin email {email} does not exist, cannot remove.")


def is_permanent_admin_dbpath(db_path: Path, email: str) -> bool:
    """Check if an admin email is permanent."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT permanent FROM admin_emails WHERE admin_email = ?",
            (email,),
        )
        result = cursor.fetchone()
        if result:
            return bool(result[0])
    return False


def add_club_temp(db_path: Path, club_name: str, club_president: str) -> None:
    """Add club to the club table."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO club_data VALUES (?,?,?,?,?,?)",
            (club_name, club_president, "Default", "Default", "Default", "Default"),
        )
    print(f"Added club: {club_name}")


def remove_club_temp(db_path: Path, club_name: str) -> None:
    """Remove club from the club table."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "DELETE FROM club_data WHERE club_name = ?",
            (club_name,),
        )
    print(f"Removed club: {club_name}")


def assign_room_temp(db_path: Path, building: str, room_num: str, club_name: str) -> None:
    """Assign room to club in the room_log table."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO room_log (building, room_num, assigned_club) VALUES (?,?,?)",
            (building, room_num, club_name),
        )
    print(f"Assigned room: {building} {room_num} to club: {club_name}")


def remove_room_temp(db_path: Path, building: str, room_num: str) -> None:
    """Remove room assignment from the room_log table."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "DELETE FROM room_log WHERE building = ? AND room_num = ?",
            (building, room_num),
        )
    print(f"Removed room assignment: {building} {room_num}")


def get_admin_emails(db_path: Path) -> list[str]:
    """Retrieve all admin emails from the admin_emails table."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT admin_email FROM admin_emails")
        emails = [row[0] for row in cursor.fetchall()]

    return emails


def verify_admin_email(db_path: Path, email: str) -> bool:
    """Check if an email is in the admin_emails table."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT 1 FROM admin_emails WHERE admin_email = ?",
            (email,),
        )
        result = cursor.fetchone()
        return result is not None


def send_email_to_single_user(db_path: Path, user_email: str, email_content: MIMEMultipart) -> None:
    """Send an email to a specific user email."""
    configure(db_path)
    mail_password = os.getenv("mail_password")
    mail_sender = os.getenv("mail_username")

    if not mail_password or not mail_sender:
        raise ValueError("Missing email credentials, add to .env file")
    email_content["To"] = user_email
    email_content["From"] = mail_sender
    with SMTP("smtp.gmail.com", 587) as smtp:  # TODO: CHANGE TO OUTLOOK FOR DEPLOYMENT
        smtp.starttls()
        smtp.login(mail_sender, mail_password)
        smtp.send_message(email_content)
        print(f"Sent email to {user_email}")


def send_email_to_all_admins(db_path: Path, email_content: MIMEMultipart) -> None:
    """Send an email to all admin emails."""
    configure(db_path)
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
    with SMTP("smtp.gmail.com", 587) as smtp:  # TODO: CHANGE TO OUTLOOK FOR DEPLOYMENT
        smtp.starttls()
        smtp.login(mail_sender, mail_password)
        smtp.send_message(email_content)
        print(f"Sent email to {compound_receiver}")


def send_recovery_email(user_email, recovery_link):
    """Send a recovery email to the user with their password reset link."""
    print(f"Sending recovery email to {user_email} with password")
    subject = "Club Tracker Password Recovery"
    body = f"Hello, {user_email}!\n\n"
    body += "We received a request to reset your password for the Club Tracker system.\n"
    body += "To reset your password, please click the link below:\n\n"
    body += f"{recovery_link}\n\n"
    body += "If you did not request a password reset, please ignore this email.\n\n"
    body += "Thank you, VCEA Club Tracker"
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    send_email_to_all_admins(user_email, msg)


def send_error_email(db_path: Path) -> None:
    """Send an error email to all admin emails."""
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    errors = check_data_health(db_path)
    if errors:
        subject = "Club Tracker Error Alert"
        body = f"Club Tracker System Health Report\nGenerated: {current_time}\n\n"
        body += "The following issues have been detected:\n\n"
        body += "\n".join(f"• {error}" for error in errors)
        body += "\n\nPlease review the system and take appropriate action."
    else:
        subject = "Club Tracker System Status: Healthy"
        body = f"Club Tracker System Health Report\nGenerated: {current_time}\n\n"
        body += "All systems are operating normally.\n"
        body += "Data is being received regularly.\n"
        body += "No significant errors detected.\n\n"
        body += "System is functioning as expected."
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    send_email_to_all_admins(db_path, msg)


def send_report_email(db_path: Path) -> None:
    """Send a monthly report email to all admin emails."""
    monthly_data = get_monthly_room_usage(db_path)
    room_usage = monthly_data["room_usage"]
    room_assignments = monthly_data["room_assignments"]
    report_period = monthly_data["period"]

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    subject = "Club Usage Tracker Monthly Report"

    body = "Club Usage Tracker Monthly Usage Report\n"
    body += f"Report Period: {report_period}\n"
    body += f"Generated: {current_time}\n\n"

    if not room_usage:
        body += "No usage data available for the reporting period."
    else:
        # highest and lowest rooms over past month
        highest_usage = room_usage[0]  # Already sorted DESC
        lowest_usage = room_usage[-1]  # Last item has lowest usage

        highest_room_key = f"{highest_usage[0]} {highest_usage[1]}"
        lowest_room_key = f"{lowest_usage[0]} {lowest_usage[1]}"

        # find clubs for those rooms
        highest_club, highest_president = room_assignments.get(highest_room_key, ("Unassigned", "N/A"))
        lowest_club, lowest_president = room_assignments.get(lowest_room_key, ("Unassigned", "N/A"))

        body += " HIGHEST USAGE ROOM:\n"
        body += f"   • Room: {highest_room_key}\n"
        body += f"   • Total Accesses: {highest_usage[2]}\n"
        body += f"   • Assigned Club: {highest_club}\n"
        body += f"   • Club President: {highest_president}\n\n"

        body += "LOWEST USAGE ROOM:\n"
        body += f"   • Room: {lowest_room_key}\n"
        body += f"   • Total Accesses: {lowest_usage[2]}\n"
        body += f"   • Assigned Club: {lowest_club}\n"
        body += f"   • Club President: {lowest_president}\n\n"

        body += "ROOM USAGE SUMMARY:\n"
        for building, room_num, total_accesses in room_usage[:10]:  # Top 10, maybe make configurable
            room_key = f"{building} {room_num}"
            club, president = room_assignments.get(room_key, ("Unassigned", "N/A"))
            body += f"   • {room_key}: {total_accesses} accesses ({club})\n"

        if len(room_usage) > 10:
            body += f"   ... and {len(room_usage) - 10} more rooms\n"

        total_accesses = sum(room[2] for room in room_usage)
        body += f"\n TOTAL ACCESSES: {total_accesses}\n"
        body += f" TOTAL ROOMS WITH ACTIVITY: {len(room_usage)}"

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    send_email_to_all_admins(db_path, msg)


def get_monthly_room_usage(db_path: Path) -> dict:
    """Get room usage statistics for the past month."""
    one_month_ago = datetime.now() - timedelta(days=30)
    one_month_ago_str = one_month_ago.strftime("%m/%d/%Y")

    print(one_month_ago_str)
    print(datetime.now().strftime("%m/%d/%Y"))
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            SELECT building, room_num, SUM(times_accessed) as total_accesses
            FROM input_data
            WHERE date_entered >= ?
            GROUP BY building, room_num
            ORDER BY total_accesses DESC
        """,
            (one_month_ago_str,),
        )

        room_usage = cursor.fetchall()
        print(room_usage)
        cursor = conn.execute(
            """
            SELECT rl.building, rl.room_num, rl.assigned_club, cd.club_president
            FROM room_log rl
            LEFT JOIN club_data cd ON rl.assigned_club = cd.club_name
        """
        )

        room_assignments = {f"{row[0]} {row[1]}": (row[2], row[3]) for row in cursor.fetchall()}
        print(room_assignments)
    return {
        "room_usage": room_usage,
        "room_assignments": room_assignments,
        "period": f"{one_month_ago.strftime('%m/%d/%Y')} to {datetime.now().strftime('%m/%d/%Y')}",
    }


def check_data_health(db_path: Path) -> list[str]:
    """Check for errors to report."""
    errors = []

    with sqlite3.connect(db_path) as conn:
        # check for new data coming in
        ten_days_ago = datetime.now() - timedelta(days=10)
        ten_days_ago_str = ten_days_ago.strftime("%m/%d/%Y")

        cursor = conn.execute("SELECT COUNT(*) FROM input_data WHERE date_entered >= ?", (ten_days_ago_str,))
        recent_data_count = cursor.fetchone()[0]

        if recent_data_count == 0:
            errors.append("No data has been received in the past 10 days")

        # check for database conn errors
        try:
            test_cursor = conn.execute("SELECT COUNT(*) FROM input_data")
            test_cursor.fetchone()
        except sqlite3.Error as e:
            errors.append(f"Database error: {str(e)}")

    return errors
