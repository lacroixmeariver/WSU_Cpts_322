"""Attendance tracker analytics web app."""

import csv
import datetime
import functools
import pathlib
import random
import sqlite3

import click
import flask
from werkzeug.middleware.proxy_fix import ProxyFix

from attendance_tracker.app import AttendanceTracker
from attendance_tracker.controllers.admin import ADMIN
from attendance_tracker.controllers.analytics import ANALYTICS
from attendance_tracker.controllers.auth import AUTH
from attendance_tracker.controllers.ingest import INGEST


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
    app.wsgi_app = ProxyFix(app=app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db_path = pathlib.Path("./sqlite/attendance_tracker.db")
    if not db_path.exists():  # if dir does not exist mkdir + db
        db_path.parent.mkdir(exist_ok=True)
        db_path.touch()

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
