"""Endpoints for doing admin tasks for the attendance tracker."""

from __future__ import annotations

import sqlite3

import flask

from attendance_tracker.controllers import auth
from attendance_tracker.email.emailList import add_admin_email, remove_admin_email
from attendance_tracker.types import tables

ADMIN = flask.Blueprint(
    name="admin",
    import_name=__name__,
    url_prefix="/h/admin",
)


@ADMIN.route("/home", methods=["GET"])
@auth.required
def home() -> str | flask.Response:
    """Home page for navigating to admin functions."""
    return flask.render_template(
        "admin_home.html",  # make actual home page later
    )


@ADMIN.route("/clubs", methods=["GET", "POST"])
@auth.required
def club_info() -> str:
    """View all clubs that have info saved in the system."""
    with flask.current_app.app_context():
        conn: sqlite3.Connection = flask.current_app.get_db()  # type: ignore

    query = """
        SELECT
            building, room_num, assigned_club
        FROM
            room_log
        ORDER BY
            building, room_num
        """
    clubs = conn.execute(query).fetchall()

    return flask.render_template(
        "club_search.html",
        clubs=clubs,
    )


@ADMIN.route("/club-config/<club_name>", methods=["GET", "POST"])
@auth.required
def club_config(club_name: str = "") -> str:
    """View club specific information and update."""
    with flask.current_app.app_context():
        conn: sqlite3.Connection = flask.current_app.get_db()  # type: ignore

    query = """
        SELECT
            *
        FROM
            club_data
        WHERE
            club_name = ?
        """
    # club = conn.execute(query).fetchone()
    dummy = tables.ClubData(
        club_name="Crimson Robotics",
        club_president="Derek",
        email="email",
        club_size=10,
        club_advisor="Dr. Derek",
        club_advisor_email="email",
    )
    club = conn.execute(query, (club_name,)).fetchone() or dummy

    return flask.render_template(
        "club_config.html",
        club_name=club_name,
        club=club,
    )


@ADMIN.route("/add-club", methods=["GET", "POST"])
@auth.required
def add_club():
    """Add a club to the db."""
    if flask.request.method == "POST":
        club = flask.request.form["club_name"]
        conn: sqlite3.Connection = flask.current_app.get_db()  # type: ignore
        cursor = conn.cursor()

        club_data = list(flask.request.form.values())

        cursor.execute(
            """SELECT CLUB_NAME
                FROM CLUB_DATA
                where CLUB_NAME=?""",
            (club,),
        )

        result = cursor.fetchone()
        if result:
            flask.flash("Club already exists!")
        else:
            cursor.execute(
                "INSERT INTO CLUB_DATA\
                VALUES (?,?,?,?,?,?)",
                club_data,
            )
            conn.commit()
        location = flask.url_for("admin.club_config", club_name=club)
        return flask.redirect(location)
    return flask.render_template("add_club.html")


@ADMIN.route("/assign-room-to-club", methods=["GET", "POST"])  # type: ignore
@auth.required
def assign_club():
    """Assign a room to a club."""
    conn: sqlite3.Connection = flask.current_app.get_db()  # type: ignore
    cursor = conn.cursor()
    if flask.request.method == "POST":
        club = flask.request.form["assigned_club"]
        building = flask.request.form["building"]
        room_num = flask.request.form["room_num"]

        cursor.execute(
            """SELECT ASSIGNED_CLUB
                FROM ROOM_LOG
                WHERE building = ? AND room_num = ?""",
            (building, room_num),
        )

        result = cursor.fetchone()

        if result:
            return flask.redirect(flask.url_for("admin.club_info"))
        else:
            cursor.execute(
                """INSERT INTO room_log
            (building, room_num, assigned_club) VALUES (?,?,?)
            """,
                (building, room_num, club),
            )
        conn.commit()
        return flask.redirect(flask.url_for("admin.club_info"))

    cursor.execute("SELECT club_name FROM club_data ORDER BY club_name")
    clubs = [row[0] for row in cursor.fetchall()]
    return flask.render_template("assign_club.html", club=clubs)


@ADMIN.route("/dashboard")  # type: ignore
def admin_profile():
    """Go to user dashboard."""
    auth = "uid" in flask.session
    un = flask.session.get("uid")

    return flask.render_template("admin_home.html", authenticated=auth, user=un)


@ADMIN.route("/email-list", methods=["GET", "POST"])
def display_admin_emails():
    """Manipulate admin email list."""
    with flask.current_app.app_context():
        conn: sqlite3.Connection = flask.current_app.get_db()  # type: ignore

    if flask.request.method == "POST":
        action = flask.request.form.get("action")
        if action == "add":
            new_email = flask.request.form.get("new_email")
            is_permanent = flask.request.form.get("permanent") == "on"

            if new_email:
                add_admin_email(conn, new_email, is_permanent)
        elif action == "remove":
            selected_email = flask.request.form.get("selected_email")
            if selected_email:
                print(selected_email)
                remove_admin_email(conn, selected_email)
        return flask.redirect(flask.url_for("admin.display_admin_emails"))
    query = """
            SELECT
                admin_email
            FROM
                admin_emails
            """
    email_list = conn.execute(query).fetchall()
    emails = [row[0] for row in email_list]
    return flask.render_template(
        "display_admin_emails.html",
        list=emails,
    )
