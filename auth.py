import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from database.data_manager import DataManager


bp = Blueprint("auth", __name__, url_prefix="/auth")
dm = DataManager()


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        if g.user.type_ == "admin":
            return view(**kwargs)

        abort(401, "You are not authorized to visit this page")
    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        user_id = None

    if user_id is None:
        g.user = None
    else:
        g.user = (
            dm.get_user_id(user_id=user_id)
        )


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        error = None
        user = dm.get_user_email(email)

        if user is None:
            error = "Incorrect username or password"
        elif not check_password_hash(user.password, password):
            error = "Incorrect username or password"

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for('views.index'))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/user")
def user():
    return render_template("auth/user.html")


@bp.route("/user/update", methods=["POST"])
def update_user():
    role = request.form.get("role")
    old_password = request.form.get("old-password")
    new_password = request.form.get("new-password")
    message = ""

    if not check_password_hash(g.user.password, old_password):
        message = "Current password doesn't match"

    if not message and not new_password:
        message = "No new password was provided"

    if not old_password:
        user_ = dm.get_user_id(g.user.id)
        if user_.role != role:
            user_.role = role
            if dm.update_user(user_)[0]:
                g.user.role = role
                message = "Role updated"
            else:
                message = "Role couldn't be updated"

    if not message:
        user_ = dm.get_user_id(g.user.id)
        user_.role = role
        user_.password = generate_password_hash(new_password)
        if dm.update_user(user_)[0]:
            message = "Password updated"
        else:
            message = "Password couldn't be updated"

    flash(message)
    return render_template("auth/user.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for('views.index'))
