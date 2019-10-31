import requests
import jsonpickle

from flask import render_template, request, Blueprint

from .forms import MessageForm
from ..utils.utils import create_proper_url_string
from ..utils.constants import DEFAULT_HOST, DEFAULT_PORT, CHAIN_ENDPOINT, ADD_ENDPOINT, MESSAGE_PARAM


blueprint = Blueprint("blockchain_blueprint", __name__, template_folder="templates", static_folder="static")

def format_timestamp(timestamp):
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


@blueprint.route("/", methods=["GET", "POST"])
def main():
    """
    Root endpoint (``/``). Shows a representation of the current chain.
    """

    try:
        form = MessageForm(request.form)

        if request.method == "POST" and form.validate():
            requests.put(create_proper_url_string((DEFAULT_HOST, DEFAULT_PORT), ADD_ENDPOINT), params={MESSAGE_PARAM: form.message.data})

        response = requests.get(create_proper_url_string((DEFAULT_HOST, DEFAULT_PORT), CHAIN_ENDPOINT))
        chain = jsonpickle.decode(response.json()["chain"])

        return render_template("index.html", chain=chain, format_timestamp=format_timestamp, form=form)

    except Exception as error:
        print(error)
        return render_template("error.html")


@blueprint.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    """
    Catches all not declared endpoints and shows 404 error page.

    Args:
            path (str): Path that cannot be found
    """

    return render_template("404.html")
