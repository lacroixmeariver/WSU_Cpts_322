"""Attendance tracker analytics web app."""

import csv
import datetime
import functools
import pathlib
import random
import sqlite3

import click
import flask
from flask_apscheduler import APScheduler

from attendance_tracker.app import AttendanceTracker
from attendance_tracker.controllers.admin import ADMIN
from attendance_tracker.controllers.analytics import ANALYTICS
from attendance_tracker.controllers.auth import AUTH
from attendance_tracker.controllers.ingest import INGEST
from attendance_tracker.email.emailList import send_error_email, send_report_email


def _init_db(db_path: pathlib.Path) -> None:
    """**Overwrite db with table schema, fully deleting tables**."""
    init_db = pathlib.Path("./sqlite/init.sql")

    with (
        sqlite3.connect(db_path) as conn,
        init_db.open("r", encoding="utf-8") as sql,
    ):
        script = sql.read()
        conn.executescript(script)
        show_tables = "SELECT name FROM sqlite_master WHERE type = 'table';"
        print(f"created tables: {conn.execute(show_tables).fetchall()}\n")


def _load_from_email(db_path: pathlib.Path) -> None:
    """Check the email and download csvs, then loads them into the db."""
    import attendance_tracker.email.download_csv as download_csv

    download_csv._load_from_email(db_path)


def _send_email_test(db_path: pathlib.Path) -> None:
    """Send a test email to all admin emails."""
    import attendance_tracker.email.emailList as emailList

    emailList.remove_club_temp(db_path, "Demo Club 1")
    emailList.add_club_temp(db_path, "Demo Club 1", "dylan")
    emailList.assign_room_temp(db_path, "Dana", "215", "Demo Club 1")
    emailList.remove_admin_email(db_path, "dylan.kopitzke@wsu.edu")
    emailList.add_admin_email(db_path, "dylan.kopitzke@wsu.edu")
    emailList.send_error_email(db_path)
    emailList.send_report_email(db_path)


def _model_data_with_date():
    room_names = ["Demo Club 1", "Demo Club 2", "Demo Club 3"]
    today = datetime.date.today()
    date_list = [today + datetime.timedelta(days=i) for i in range(0, 365, 7)]

    # splitting the known rooms/numbers we have
    data = {
        "Dana": [3, 51, 117, 213, 215, 216],
        "Dana hall room": [216, 242],
        "Dana hall rm": [246, 306],
        "EEME": [207],
        "Sloan": [242, 327],
    }
    listed: list[tuple[str, int]] = []
    for key, values in data.items():
        listed.extend([(key, v) for v in values])

    out_path = pathlib.Path("./docs/exampleDataWithDates.csv")

    with out_path.open("w", newline="") as out_file:
        csv_writer = csv.writer(out_file)

        header = [
            "Building",
            "RoomNum",
            "RoomName",
            "PatronNum",
            "TotalPassed",
            "TotalFailed",
            "Date",
        ]
        csv_writer.writerow(header)
        for date in date_list:
            for location in listed:
                building, room = location
                patron_num_col = random.randint(0, 35)
                total_allowed = random.randint(0, patron_num_col)
                total_denied = patron_num_col - total_allowed
                row = [
                    building,
                    room,
                    random.choice(room_names),
                    patron_num_col,
                    total_allowed,
                    total_denied,
                    date.strftime("%Y-%m-%d"),
                ]
                csv_writer.writerow(row)


def create_app() -> AttendanceTracker:
    """Entry point for flask app."""
    app = AttendanceTracker(__name__, instance_relative_config=True)
    scheduler = APScheduler()

    db_path = pathlib.Path("./sqlite/attendance_tracker.db")
    if not db_path.exists():  # if dir does not exist mkdir + db
        db_path.parent.mkdir(exist_ok=True)
        db_path.touch()

    # schedule email jobs for first min of 9am on mondays and 1st of month
    scheduler.add_job(
        func=send_error_email,
        trigger="cron",
        id="weekly_email_start",
        day_of_week=0,
        hour=9,
        minute=0,
        args=[db_path],
    )
    scheduler.add_job(
        func=send_report_email,
        trigger="cron",
        id="monthly_email_start",
        day=1,
        hour=9,
        minute=0,
        args=[db_path],
    )
    # schedule email job for every day at 3am to load new data
    scheduler.add_job(
        func=_load_from_email,
        trigger="cron",
        id="daily_email_load",
        hour=3,
        minute=0,
        args=[db_path],
    )
    scheduler.start()

    # get secret to save in config for session handling
    with pathlib.Path("./.env").open("r", encoding="utf-8") as env:
        super_secret_key = env.read().strip()

    # register close db to happen at clean up
    app.teardown_appcontext(app.close_db)
    app.config.from_mapping(
        DATABASE=db_path,
        SECRET_KEY=super_secret_key,
    )
    init_db_cmd = click.Command(
        "init-db",
        callback=functools.partial(_init_db, db_path),
    )
    app.cli.add_command(init_db_cmd)  # register init-db as flask cli cmd

    load_db_cmd = click.Command(
        "load-from-email",
        callback=functools.partial(_load_from_email, db_path),
    )
    app.cli.add_command(load_db_cmd)  # register data load as flask cmd

    send_email_cmd = click.Command(
        "send-email-test",
        callback=functools.partial(_send_email_test, db_path),
    )
    app.cli.add_command(send_email_cmd)  # register send email test as flask cmd

    generate_sample_data = click.Command(
        "gen-sample-data",
        callback=_model_data_with_date,
    )
    app.cli.add_command(generate_sample_data)  # gen sample data as flask cmd

    app.register_blueprint(ADMIN)
    app.register_blueprint(ANALYTICS)
    app.register_blueprint(AUTH)
    app.register_blueprint(INGEST)

    @app.route("/")
    def index():
        return flask.render_template(
            "index.html",
            name="INDEX",
            title="HOMEPAGE",
        )

    return app
