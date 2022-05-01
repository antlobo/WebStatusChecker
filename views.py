import datetime
import json
from datetime import date

import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly

from flask import (
    Blueprint, render_template, request
)

from auth import login_required
from database.data_manager import DataManager
from common.models import AppType

_PREFIX = "views"

bp = Blueprint("views", __name__)
dm = DataManager()


@bp.route("/")
def index():
    services, stat = dm.get_services(status=None)
    last_time_online, result = dm.get_last_active_time()
    last_time_online_dict = {}
    if last_time_online:
        last_time_online_dict = {v: k for k, v in last_time_online}
    return render_template("views/index.html", services=services, last_time_online=last_time_online_dict)


@bp.route("/service/<int:app_id>", methods=["GET", "POST"])
@login_required
def service(app_id):
    service_, stat = dm.get_service(app_id=app_id)
    return render_template("views/service.html", service=service_)


@bp.route("/service/<int:app_id>/callback", methods=["GET", "POST"])
@login_required
def cb(app_id):
    if not isinstance(app_id, int):
        return_dict = {
            "logs": {},
            "graph_json": {}
        }
        return json.dumps(return_dict, indent=4, sort_keys=True, default=str)

    start_date = request.form.get("log-start") or request.args.get("log-start")
    end_date = request.form.get("log-end") or request.args.get("log-end")

    try:
        start_date = date.fromisoformat(start_date)
    except (ValueError, TypeError):
        start_date = None

    try:
        end_date = date.fromisoformat(end_date)
    except (ValueError, TypeError):
        end_date = None

    if not isinstance(start_date, date) and not isinstance(end_date, date):
        start_date = date.today()

    logs, graph_json = get_logs_and_graph(app_id=app_id, start_date=start_date, end_date=end_date)

    return_dict = {
        "logs": json.dumps([log.to_dict() for log in logs], sort_keys=True, default=str),
        "graph_json": graph_json
    }

    return json.dumps(return_dict, indent=4, sort_keys=True, default=str)


@bp.app_template_filter("last_online")
def template_last_online(status_date: datetime.datetime):
    now = datetime.datetime.now()
    difference = now - status_date
    seconds = abs(int(difference.total_seconds()))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def get_logs_and_graph(app_id, start_date, end_date):
    graph_json = {}
    df = None
    logs, _ = dm.get_logs(app_id=app_id, start_date_=start_date, end_date_=end_date)
    service_, _ = dm.get_service(app_id=app_id)

    if logs:
        df = pd.DataFrame([log.to_dict() for log in logs])

    if df is not None and service_.app_type == AppType.T_SENSOR.value:
        df["other_data"] = df["other_data"].str.split("-", expand=True)[1]

    try:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df["status_date"],
                                 y=df["status"],
                                 line=dict(color="blue"),
                                 mode='lines+markers',
                                 name='Status',
                                 ), secondary_y=False)
        if service_.app_type == AppType.T_SENSOR.value:
            fig.add_trace(go.Scatter(x=df["status_date"],
                                     y=df["other_data"],
                                     line=dict(color="red"),
                                     mode='markers',
                                     name='Temperature',
                                     ), secondary_y=True)
    except (ValueError, TypeError):
        fig = None

    if fig:
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return logs, graph_json
