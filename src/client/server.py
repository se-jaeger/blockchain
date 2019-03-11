from multiprocessing import Queue, Pipe
from flask import Flask, jsonify, request

from src.utils.constants import *


def start_server(queue: Queue):

    app = Flask(__name__)


    @app.route(ADD_ENDPOINT, methods=["PUT"])
    def add_message():

        message = request.args.get("message")

        if not message:
            return jsonify({"message": "No Message added! - Missing data..."}), HTTP_BAD

        queue.put_nowait({ADD_KEY: message})

        response = {"message": "Message added!",
                    "more_information": "Will be mined in a future block."
                    }

        return jsonify(response), HTTP_OK


    @app.route(CHAIN_ENDPOINT, methods=["GET"])
    def send_chain():

        parent_connection, child_connection = Pipe()
        queue.put_nowait({SEND_CHAIN_KEY: parent_connection})

        response = child_connection.recv()

        return jsonify(response), HTTP_OK


    @app.route(NEIGHBOURS_ENDPOINT, methods=["GET"])
    def send_neighbours():

        parent_connection, child_connection = Pipe()
        queue.put_nowait({SEND_NEIGHBOURS_KEY: parent_connection})

        response = child_connection.recv()

        return jsonify(response), HTTP_OK


    @app.route(DATA_ENDPOINT, methods=["GET"])
    def send_data():

        parent_connection, child_connection = Pipe()
        queue.put_nowait({SEND_DATA_KEY: parent_connection})

        response = child_connection.recv()

        return jsonify(response), HTTP_OK


    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>", methods=["GET", "POST"])
    def catch_all(path):
        return jsonify({"message": "'{}' is not a valid endpoint!".format(path)}), HTTP_NOT_FOUND


    app.run(HOST_DEFAULT, PORT_DEFAULT)