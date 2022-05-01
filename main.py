import json
import os
import logging.config
from typing import NoReturn

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def setup_logging(
        default_path='logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG') -> NoReturn:
    """
    Configure logging capabilities
    :param default_path: path to search for the logging configuration
    :param default_level: default level to log
    :param env_key: if using environment variable instead of default_path
    :return: it doesn't return a value
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", text=e), 404


@app.errorhandler(401)
def page_not_found(e):
    return render_template("error.html", text=e), 401


if __name__ == "__main__":
    load_dotenv()
    setup_logging()
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    from auth import bp as auth_bp
    from views import bp as views_bp
    from admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(admin_bp)

    app.run("0.0.0.0", debug=True)
