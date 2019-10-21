import logging

from multiprocessing import Queue, Pipe
from flask import Flask, jsonify, request

from utils.constants import *


logger = logging.getLogger(__name__)


def start_server(queue: Queue, port: int):

    logger.debug(f"Create and init server ...")

    app = Flask(__name__)
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.logger.disabled = True


    @app.route(ADD_ENDPOINT, methods=["PUT"])
    def add_message():

        message = request.args.get(MESSAGE_PARAM)
        logger.debug(f"'{request.method}' at endpoint: '{ADD_ENDPOINT}' with message: '{message}'")

        if not message:

            logger.debug(f"URL Parameter: '{MESSAGE_PARAM}' is missing.")

            response = {"message": "No Message added!",
                        "more_information": "Missing data."
                        }

            return jsonify(response), HTTP_BAD

        queue.put_nowait((ADD_KEY, message))

        response = {"message": "Message added!",
                    "more_information": "Will be mined in a future block."
                    }

        logger.debug(f"Message added. - HTTP status: '{HTTP_OK}'")
        return jsonify(response), HTTP_OK


    @app.route(CHAIN_ENDPOINT, methods=["GET"])
    def send_chain():

        logger.debug(f"'{request.method}' at endpoint: '{CHAIN_ENDPOINT}'")

        parent_connection, child_connection = Pipe()
        queue.put_nowait((SEND_CHAIN_KEY, parent_connection))

        response = child_connection.recv()

        logger.debug(f"Got chain -> send as response.. - HTTP status: '{HTTP_OK}'")
        return jsonify(response), HTTP_OK


    @app.route(NEIGHBOURS_ENDPOINT, methods=["GET"])
    def send_neighbours():

        logger.debug(f"'{request.method}' at endpoint: '{NEIGHBOURS_ENDPOINT}'")

        parent_connection, child_connection = Pipe()
        queue.put_nowait((SEND_NEIGHBOURS_KEY, parent_connection))

        logger.debug(f"Got neighbours -> send as response.. - HTTP status: '{HTTP_OK}'")
        response = child_connection.recv()

        return jsonify(response), HTTP_OK


    @app.route(DATA_ENDPOINT, methods=["GET"])
    def send_data():

        logger.debug(f"'{request.method}' at endpoint: '{DATA_ENDPOINT}'")

        parent_connection, child_connection = Pipe()
        queue.put_nowait((SEND_DATA_KEY, parent_connection))

        response = child_connection.recv()

        logger.debug(f"Got unprocessed data -> send as response.. - HTTP status: '{HTTP_OK}'")
        return jsonify(response), HTTP_OK


    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>", methods=["GET", "POST"])
    def catch_all(path):

        logger.warning(f"Invalid endpoint - '{request.method}' at endpoint: '{path}'")
        return jsonify({"message": "'{}' is not a valid endpoint!".format(path)}), HTTP_NOT_FOUND


    logger.debug(f"Server created and initialized.")
    app.run(host=DEFAULT_HOST, port=port)
    