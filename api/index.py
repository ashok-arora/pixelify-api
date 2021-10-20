from flask import Flask

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "Pixelify backend API. Made using Flask and Python.", 200


@app.route("/ping", methods=["GET"])
def ping():
    return "pong!", 200


@app.route("/encrypt", methods=["POST"])
def encrypt():
    return "hehe", 200


@app.route("/decrypt", methods=["POST"])
def decrypt():
    return "not hehe", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
