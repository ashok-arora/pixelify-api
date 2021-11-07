import base64
import bcrypt
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request
from io import BytesIO
import numpy as np
import pickle
import piexif
from PIL import Image
import random
import uuid
import os

from api.caesar import Caesar

# from cryptography.fernet import Fernet

# decrypt file using secret key
# key = os.environ.get("PIXELIFY_KEY")
# f = Fernet(key)

# with open("./serviceAccountKey.enc", "rb") as encrypted_file:
#     encrypted = encrypted_file.read()

# decrypted = f.decrypt(encrypted)
# with open("./serviceAccountKey.json", "wb") as decrypted_file:
#     decrypted_file.write(decrypted)


# Use a service account

data = {'type': 'service_account', 'project_id': 'blacksheep-9a512', 'private_key_id': 'd1c69e6abc3186db08dbc7c626861a35b068ab7e', 'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCzGsedmlXHquOH\ni06Sl9i9iS4zW+llmrLxefB4OoJc/w1bn2ITC1qp9zLksQZNeAUvu3bxa2AsUOTt\n1yBs7uxMPpJosb7fvXZFHu3y1LJz8pCpSItYLp7pUG98gq3F/je30LugWuxmMgh4\nfgQXSlgTB/c9ePs3XZMPSY5ozqTn5PabZLZL3lbTZiuAYFtyRpvEOcVQsnQuvQpy\n0jvLLy084YRWgw83su0DsGwhUcs9aq15BGDkduLmuozdFW+IR24KVp9nLotopopa\n2GLDai925tVdu/bmGLL24IApqOpmAe394HQms2gVOAmI7M1NZ5iv/BCNeTj+tn8t\nVABCqdLFAgMBAAECggEADtzdjMwWazvYptJeIlccgtoD7fomG6rjR5utY2TDlbEK\nrDxFOLxb+TfMzuKL2djoYUYmwDD/aZ4K6VvNUozfKhKVNr/tTYbc7i57Y4fYCTwr\nWgjtm1M/F7B3l/cGMaR/fi8BqvRwoqhrQIiAkWg3d9jU4RKNklIfFoktmq/vSlj3\nu4e4kXIAdW1aeEFZbYzL2C1ZAVcUumAdulIoHcz9Q/QNS0owucjODRjUiXYJL4kw\nEkEjP3zP7wrPfzSzST+WVfEM1nBLfRnzB6lM858iaqb5/d0112Yql50GTgExXf5E\nYD11Vl/KgL3xEhPZ9iI6AD4JBn0zq3jaCW4II717/wKBgQDbPCq3zw0+EnxJzIP0\nOvKle4UIrjyknzrV8SWU9WaDBc9MRTKIjRgCFyzgcs4WRdoLhKgrDkWG8m/jjAht\n1whqbiHxfS1hoMeKLi/yv/2EiSr4EzxgHi+e4lNnYOZSfTuVU3hsJYD5EzKSXxUJ\nIxe2/FelE7UhOZPsE5zA1X4bdwKBgQDRI8zymBdzNJPu8rveMeFw+liPyjVRt1a0\ntaWqG8xVWOyk4a26PBpHNngf2Zr0FkMBlWgSgN9RFmg+gombJhuctblckxSJY3JC\nNgJ7CCaxk2h4TlNC3sl4WoSUpvx5ZeKkhYKHb5kOUiPh9+1GuDmEJeJCc5C646L2\naKDiqJ3aowKBgBqeKn2YqP3xVp/LMfY0NgO7hIJyTTCbmJQjLDHyvZiI2wtil2kW\n4GRYlf1GUxlHL9sYJybbG7vvsYAKH3felMn/RyW/0gO5dqCjTPUHNGukD9CA3WK6\nJ4P97KxvimdXhyVxNfzDbO5Q02IMI0yxsw5nguirBOHc0MXn9689/IqvAoGAEE6Q\nTmIZgfwZhMocZ+jPwTVj7mI/4g0/j3uSXT8poYX7faezGhBRpDfVCfa3pEyQEPGL\nWdX+k54Bps4a2KQSBxgMSfGV6lh8sjjv3JP4IGR0At1olJA2eVHlgIm8qeKN13Ip\niVHkRz+UWKwyLg9zPKCPkcrdABV7wWbLFKE9Ha0CgYEA1Ds/uIqldrZHqgcYIIRo\niJxPUwkYOy/FS15Z95kp0QqzkbWhET3G9iCmDDgp78qgi7IcMrLUFW+bj2dfs5y8\nc/l6rlyrArdFsSxEIbapu6g+UHhRTwsnjCztpp4MmtZEp5XAaN9P3FelW9QY6GLU\n6JkN0jVDcRg/H9SJP7OEYJ8=\n-----END PRIVATE KEY-----\n', 'client_email': 'firebase-adminsdk-frsqs@blacksheep-9a512.iam.gserviceaccount.com', 'client_id': '113972597733055985606', 'auth_uri': 'https://accounts.google.com/o/oauth2/auth', 'token_uri': 'https://oauth2.googleapis.com/token', 'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs', 'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-frsqs%40blacksheep-9a512.iam.gserviceaccount.com'}

cred = credentials.Certificate(data)
firebase_admin.initialize_app(cred)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "Pixelify backend API. Made using Flask and Python.", 200


@app.route("/ping", methods=["GET"])
def ping():
    return "pong!", 200


@app.route("/encrypt", methods=["POST"])
def encrypt():
    params = request.json
    password = params['password']
    image = params['image']
    cipher = params['cipher']
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
    image_head = image[:image.index(',')+1]
    image = image[image.index(',')+1:]
    base64_decoded = base64.b64decode(image)
    img = Image.open(BytesIO(base64_decoded))
    img = np.array(img)

    # encrypt
    cipher = Caesar(key=key)
    cipher.encrypt(img)

    # adding id to metadata
    data = pickle.dumps(id)
    exif_ifd = {piexif.ExifIFD.MakerNote: data}
    exif_dict = {"Exif": exif_ifd}
    exif_dat = piexif.dump(exif_dict)

    # convert encrypted image to base64
    pil_img = Image.fromarray(img)
    buff = BytesIO()
    pil_img.save(buff, format="JPEG", exif=exif_dat)
    encrypted_image = base64.b64encode(buff.getvalue()).decode("utf-8")
    encrypted_image = image_head+encrypted_image

    return encrypted_image, 200


@app.route("/decrypt", methods=["POST"])
def decrypt():
    params = request.json
    password = params['password']
    image = params['image']
    cipher = params['cipher']
    # hash password using bcrypt

    # check if hash exists

    # if hash exists, extract id from image metadata

    # find corresponding cipher and key from firestore

    # decrypt

    # return decrypted base64 image

    return "not hehe", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
