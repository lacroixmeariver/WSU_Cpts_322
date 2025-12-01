"""Endpoints that allows users to log into the system."""

from __future__ import annotations

import functools
import hashlib
import sqlite3
from typing import Callable

import flask

AUTH = flask.Blueprint(
    name="auth",
    import_name=__name__,
    url_prefix="/h/auth",
)


def required(func: Callable) -> Callable | flask.Response:
    """Redirects to login page if user is not authenticated."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if flask.session.get("uid") is None:
            return flask.redirect(location=flask.url_for("auth.login"))  # type: ignore
        return func(*args, **kwargs)

    return wrapper


@AUTH.route("/login", methods=["GET", "POST"])
def login() -> str | flask.Response:
    """Render the login view page.

    Name and title serve as variables for templates.
    """
    un: str = flask.request.form.get("uid") or ""  # un/pw not validated by form
    if flask.request.method == "POST":
        with flask.current_app.app_context():
            conn: sqlite3.Connection = flask.current_app.get_db()  # type: ignore
        pw = flask.request.form.get("pw") or ""  # required
        pw = hashlib.sha256(pw.encode(encoding="utf-8")).hexdigest()

        result = conn.execute(  # returns a singleton tuple with password_
            "SELECT password_ FROM auth WHERE username = ?", (un,)
        ).fetchone()
        match result or None:
            case (actual_pw, *_) if actual_pw == pw:
                flask.session["uid"] = un
                flask.session["pw"] = actual_pw
            case _:
                pass  # TODO (Any): Add error messages in future front end pr

    # fall thru or GET
    un = flask.session.get("uid") or ""
    return flask.render_template(
        "login.html",
        name="LOGIN PAGE",
        title="LOGIN VIEW",
        action="Sign In",
        username=un,
        authenticated=flask.session.get("uid") is not None,
    )


@AUTH.route("/sign-up", methods=["GET", "POST"])
def sign_up() -> str:
    """Register username/password in the DB."""
    if flask.request.method == "GET":
        return flask.render_template(
            "login.html",
            name="LOGIN PAGE",
            title="LOGIN VIEW",
            action="Register",
            sign_up=True,
        )

    # must be POST
    un: str = flask.request.form.get("uid") or ""  # un/pw not validated by form
    pw = flask.request.form.get("pw") or ""  # required
    with flask.current_app.app_context():
        conn: sqlite3.Connection = flask.current_app.get_db()  # type: ignore

    query = "SELECT username FROM auth WHERE username = ?"
    r = conn.execute(query, (un,)).fetchone()
    if r is None:
        pw = hashlib.sha256(pw.encode(encoding="utf-8")).hexdigest()
        query = "INSERT INTO auth (username, password_) VALUES (?, ?)"
        conn.execute(query, (un, pw)).fetchall()
        conn.commit()
        flask.session["uid"] = un
        flask.session["pw"] = pw

    return flask.render_template(
        "login.html",
        name="LOGIN PAGE",
        title="LOGIN VIEW",
        action="Login",
        username=un,
        authenticated=flask.session.get("uid") is not None,
    )


@AUTH.route("/log-out", methods=["POST"])
def log_out() -> flask.Response:
    """End current user session and redirect to login page."""
    flask.session.pop("uid")
    flask.session.pop("pw")

    return flask.redirect(location=flask.url_for("auth.login"))  # type:ignore
