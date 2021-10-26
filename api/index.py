import base64
import bcrypt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask
from io import BytesIO
import numpy as np
import pickle
import piexif
from PIL import Image
import random
import uuid

from caesar import Caesar


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

    # generate key for cipher
    key = random.randint(0, 255)

    # store id, cipher and key in firestore
    doc_ref = db.collection("id-cipher-key").document(id)
    doc_ref.set({"id": id, "cipher": cipher, "key": key})

    # convert image to numpy array
    base64_decoded = base64.b64decode(image)
    img = Image.open(BytesIO(base64_decoded))
    img = np.array(img)

    # encrypt
    cipher = Caesar(key=key)
    cipher.encrypt(img)

    # adding id to metadata
    data = pickle.dumps(id)
    exif_ifd = {piexif.ExifIFD.MakerNote: data}
    exif_dict = {'Exif': exif_ifd}
    exif_dat = piexif.dump(exif_dict)

    # convert encrypted image to base64
    pil_img = Image.fromarray(img)
    buff = BytesIO()
    pil_img.save(buff, format='JPEG', exif=exif_dat)
    encrypted_image = base64.b64encode(buff.getvalue()).decode('utf-8')

    return encrypted_image, 200


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
