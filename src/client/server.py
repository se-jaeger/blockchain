import jsonpickle

from flask import Flask, jsonify, request

from src.utils.constants import *


def start_server(miner):

    app = Flask(__name__)


    @app.route(ADD_ENDPOINT, methods=["PUT"])
    def add_message():

        message = request.args.get("message")

        if not message:
            return jsonify({"message": "No Message added! - Missing data..."}), HTTP_BAD


        miner.new_message(message)

        response = {"message": "Message added!",
                    "more_information": "Will be mined in a future block."
                    }

        return jsonify(response), HTTP_OK


    @app.route(CHAIN_ENDPOINT, methods=["GET"])
    def send_chain():

        response = {
            'chain': jsonpickle.encode(miner.blockchain.chain),
            'length': len(miner.blockchain.chain),
        }
        return jsonify(response), HTTP_OK


    @app.route(NEIGHBOURS_ENDPOINT, methods=["GET"])
    def send_neighbours():

        return jsonify(jsonpickle.encode(miner.neighbours)), HTTP_OK


    @app.route(DATA_ENDPOINT, methods=["GET"])
    def send_data():

        return jsonify(jsonpickle.encode(miner.unprocessed_data)), HTTP_OK


    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>", methods=["GET", "POST"])
    def catch_all(path):
        return jsonify({"message": "'{}' is not a valid endpoint!".format(path)}), 404


    app.run(HOST_DEFAULT, PORT_DEFAULT)