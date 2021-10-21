import uuid
import random
import string

import bcrypt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask


# Use a service account
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "Pixelify backend API. Made using Flask and Python.", 200


@app.route("/ping", methods=["GET"])
def ping():
    return "pong!", 200


@app.route("/encrypt", methods=["POST"])
def encrypt(password, image, cipher):

    # firestore client
    db = firestore.client()

    # hash password using bcrypt
    salt = bcrypt.gensalt(rounds=12)
    password_bytes = str.encode(password)
    hash = bcrypt.hashpw(password_bytes, salt)

    # generate id, firestore doesn't support auto-increment id
    id = str(uuid.uuid4())

    # store hash and id in firestore
    doc_ref = db.collection("hash-id").document(id)
    doc_ref.set({"hash": hash, "id": id})

    # generate key for the id
    key = ''.join(random.choices(string.ascii_lowercase, k=64))

    # store id, cipher and key in firestore
    doc_ref = db.collection("id-cipher-key").document(id)
    doc_ref.set({"id": id, "cipher": cipher, "key": key})

    # encrypt

    # store id in encrypted image

    # return encrypted base64 image

    return "hehe", 200


@app.route("/decrypt", methods=["POST"])
def decrypt(password, image, cipher):

    # hash password using bcrypt

    # check if hash exists

    # if hash exists, extract id from image metadata

    # find corresponding cipher and key from firestore

    # decrypt

    # return decrypted base64 image

    return "not hehe", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
