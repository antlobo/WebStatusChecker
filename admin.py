import json

from flask import (
    Blueprint, g, flash, redirect, render_template, request, url_for
)

from werkzeug.security import generate_password_hash

from auth import admin_required
from common.models import User, Service, AppType
from database.data_manager import DataManager

bp = Blueprint("admin", __name__, url_prefix="/admin")
dm = DataManager()
routes = [("List or Update users", "list_users", "Option to show all users, update their attributes and status"),
          ("Add user", "add_user", "Option to add a new user"),
          ("List or Update services", "list_services", "Option to show all services, update their attributes and status"),
          ("Add service", "add_service", "Option to add a new service")]


@bp.route("/")
@admin_required
def index():
    return render_template("admin/index.html", routes=routes)


@bp.route("/users")
@admin_required
def list_users():
    users, _ = dm.get_users()
    return render_template("admin/users_list.html", users=users)


@bp.route("/user/add", methods=("GET", "POST"))
@admin_required
def add_user():
    """Register a new user.
    Validates that the username is not already taken. Hashes the
    password for security.
    """
    message = ""
    created = False

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        role = request.form.get("role")
        type_ = request.form.get("type")

        if type_ not in ("user", "admin"):
            type_ = "user"

        try:
            user = User(email=email, password=generate_password_hash(password), name=name, type_=type_, role=role)
        except ValueError as e:
            message = e.args[0]
        else:
            created, message = dm.add_user(user)

    if message:
        flash(message)
    if created:
        return redirect(url_for(".list_users"))

    return render_template("admin/user_add.html")


@bp.route("/user/<int:user_id>")
@admin_required
def show_user(user_id):
    user = dm.get_user_id(user_id)
    return render_template("admin/user_update.html", user=user)


@bp.route("/user/<int:user_id>/update", methods=["POST"])
@admin_required
def update_user(user_id):
    user = dm.get_user_id(user_id)
    updated = ""
    message = ""

    if isinstance(user, User):
        user.name = request.form.get("name")
        user.role = request.form.get("role")

        try:
            user.type_ = request.form.get("type")
        except ValueError as e:
            message = e.args[0]

        if not message:
            updated, message = dm.update_user(user)
    else:
        message = "There was not possible to update user"

    return_dict = {
        "updated": updated,
        "message": message
    }

    return json.dumps(return_dict)


@bp.route("/user/<int:user_id>/update_status", methods=["POST"])
@admin_required
def update_user_status(user_id):
    message = ""
    status = ""
    updated = False

    try:
        user_id = int(user_id)
    except TypeError as e:
        message = "It wasn't provided a valid id"
    else:
        if user_id != g.user.id:
            try:
                status = dm.get_user_id(user_id).status
            except (TypeError, ValueError):
                message = "It wasn't provided a valid id"
                status = ""

            if status == "active":
                status = "inactive"
            elif status == "inactive":
                status = "active"

            if status in ["active", "inactive"]:
                updated, message = dm.update_user_status(user_id, status)

    return_dict = {
        "updated": updated,
        "status": status,
        "message": message
    }
    return json.dumps(return_dict, indent=4)


@bp.route("/services")
@admin_required
def list_services():
    services, _ = dm.get_services(status=None)
    return render_template("admin/services_list.html", services=services)


@bp.route("/service/add", methods=("GET", "POST"))
@admin_required
def add_service():
    """Register a new user.
    Validates that the username is not already taken. Hashes the
    password for security.
    """
    message = ""
    created = False

    if request.method == "POST":
        name = request.form.get("name", default="", type=str)
        description = request.form.get("description", default="", type=str)
        url = request.form.get("url", default="", type=str)
        route = request.form.get("route", default="", type=str)
        user = request.form.get("user", default="", type=str)
        password = request.form.get("password", default="", type=str)
        app_type = request.form.get("type", default="", type=str)
        other_data1 = request.form.get("other_data1", default="", type=str)
        other_data2 = request.form.get("other_data2", default="", type=str)
        other_data3 = request.form.get("other_data3", default="", type=str)
        other_data4 = request.form.get("other_data4", default="", type=str)
        other_data5 = request.form.get("other_data5", default="", type=str)

        if not name:
            message = "Name is required."
        elif not url:
            message = "URL is required."
        elif not route:
            message = "Route is required."
        elif not app_type:
            message = "App type is required."

        app_type = AppType.get_app_type(app_type)

        if not message:
            try:
                service = Service(name=name,
                                  description=description,
                                  url=url,
                                  route=route,
                                  user=user,
                                  password=password,
                                  app_type=app_type,
                                  other_data1=other_data1,
                                  other_data2=other_data2,
                                  other_data3=other_data3,
                                  other_data4=other_data4,
                                  other_data5=other_data5)
            except ValueError as e:
                message = e.args[0]
            else:
                created, message = dm.add_service(service)

    if message:
        flash(message)

    if created:
        return redirect(url_for(".list_services"))

    return render_template("admin/service_add.html")


@bp.route("/service/<int:app_id>")
@admin_required
def show_service(app_id):
    service, _ = dm.get_service(app_id, status=None)
    return render_template("admin/service_update.html", service=service)


@bp.route("/service/<int:app_id>/update", methods=["POST"])
@admin_required
def update_service(app_id):
    service, _ = dm.get_service(app_id, status=None)
    message = ""
    updated = False

    if isinstance(service, Service):
        service.name = request.form.get("name", default="", type=str)
        service.url = request.form.get("url", default="", type=str)
        try:
            service.route = request.form.get("route", default="", type=str)
        except ValueError as e:
            message = e.args[0]
        service.user = request.form.get("user", default="", type=str)
        service.password = request.form.get("password", default="", type=str)
        try:
            service.app_type = (AppType.get_app_type(request.form.get("type", default="", type=str))).value
        except ValueError as e:
            message = e.args[0]
        service.other_data1 = request.form.get("other_data1", default="", type=str)
        service.other_data2 = request.form.get("other_data2", default="", type=str)
        service.other_data3 = request.form.get("other_data3", default="", type=str)
        service.other_data4 = request.form.get("other_data4", default="", type=str)
        service.other_data5 = request.form.get("other_data5", default="", type=str)

        if not message:
            updated, message = dm.update_service(service)

    return_dict = {
        "updated": updated,
        "message": message
    }

    return json.dumps(return_dict)


@bp.route("/service/<int:app_id>/update_status", methods=["POST"])
@admin_required
def update_service_status(app_id):
    message = ""
    updated = False

    try:
        service, message = dm.get_service(app_id)
        status = service.status
    except (TypeError, ValueError):
        status = ""

    if status == "active":
        status = "inactive"
    elif status == "inactive":
        status = "active"

    if status in ["active", "inactive"]:
        updated, message = dm.update_service_status(app_id, status)

    return_dict = {
        "updated": updated,
        "status": status,
        "message": message
    }

    return json.dumps(return_dict, indent=4)
