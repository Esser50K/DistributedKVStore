import os
import json
import logging
import waitress
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
from time import time
from threading import Thread
from queue import Queue

app = Flask(__name__)
CORS(app)

# Request Types
GET = "GET"
POST = "POST"
DELETE = "DELETE"

store = {}
persistence_worker = None
persistence_queue = None
persist_dir = ""


@app.route("/set", methods=[POST])
def set_values():
    if len(request.data) == 0:
        return BadRequest("request body is empty")

    try:
        data = json.loads(request.data)
        for k, v in data.items():
            store[k] = v
            persistence_queue.put({k: v})
    except Exception as e:
        logging.warning("failed to parse request body: %s" % e)
        return BadRequest("request body is invalid")

    return "ok"


@app.route("/get", methods=[GET])
def get_values():
    if len(request.args) == 0:
        return BadRequest("no query params given")

    if "keys" not in request.args.keys():
        return BadRequest("mandatory 'keys' query param not specified")

    keys = request.args["keys"].split(",")
    out = {}
    for key in keys:
        if key not in store.keys():
            continue

        out[key] = store[key]

    return jsonify(out)


def write(key, value):
    tmp_filename = persist_dir + "/key_"+str(int(time()))
    with open(tmp_filename, "w") as f:
        f.write(value)

    os.rename(tmp_filename, persist_dir + "/" + key)


def persist(queue: Queue):
    while True:
        data = queue.get()
        if data is None:
            return

        for k, v in data.items():
            write(k, v)


def load_persisted_data(persistence_dir):
    for file in os.listdir(persistence_dir):
        with open(persistence_dir + "/" + file, "r") as f:
            value = f.read()
            store[file] = value


def graceful_shutdown():
    if persistence_queue is not None:
        persistence_queue.put(None)

    if persistence_worker is not None:
        persistence_worker.join()


if __name__ == '__main__':
    persist_dir = os.getenv("PERSIST_DIR", "data")
    os.makedirs(persist_dir, exist_ok=True)
    load_persisted_data(persist_dir)

    queue_size = os.getenv("QUEUE_SIZE", 100)
    persistence_queue = Queue(queue_size)
    persistence_worker = Thread(target=persist, args=(persistence_queue,))
    persistence_worker.start()

    print("Starting WebServer...")
    waitress.serve(app, host='0.0.0.0', port=8080)
    print("Shutting down server...")
    graceful_shutdown()
