import requests
import jsonpickle
from flask import render_template, Blueprint

from utils.utils import create_proper_url_string
from utils.constants import DEFAULT_HOST, DEFAULT_PORT, CHAIN_ENDPOINT, HTTP_OK


blueprint = Blueprint('blockchain_blueprint', __name__, template_folder='templates', static_folder='static')

 
@blueprint.route('/')
def main():
    """
    Root endpoint (`/`). Shows a representation of the current chain.
    """
    
    try:
        response = requests.get(create_proper_url_string((DEFAULT_HOST, DEFAULT_PORT), CHAIN_ENDPOINT))
    except:
        return render_template("error.html")

    if response.status_code == HTTP_OK:
        chain = jsonpickle.decode(response.json()["chain"])

        def format_timestamp(timestamp):
            from datetime import datetime
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        return render_template("index.html", chain=chain, format_timestamp=format_timestamp)

    else:
        return render_template("error.html")


@blueprint.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    """
    Catches all not declared endpoints and shows 404 error page.

    Args:
            path (str): Path that cannot be found
    """

    return render_template("404.html")
