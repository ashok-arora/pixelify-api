import base64
import bcrypt
from cryptography.fernet import Fernet
import firebase_admin
from firebase_admin import credentials, firestore, storage
from flask import Flask, request, jsonify
from flask_cors import CORS
from io import BytesIO
import json
import numpy as np
import os
import pickle
import piexif
from PIL import Image
import uuid

from api.caesar import Caesar
from api.modified_caesar import ModifiedCaesar
from api.one_time_pad import OneTimePad
from api.transposition import Transposition


# decrypt file using secret key
key = os.environ.get('PIXELIFY_KEY')
f = Fernet(key)

with open('./serviceAccountKey.enc', 'rb') as encrypted_file:
    encrypted = encrypted_file.read()

decrypted = f.decrypt(encrypted)
with open('./serviceAccountKey.json', 'wb') as decrypted_file:
    decrypted_file.write(decrypted)


# Use a service account
cred = credentials.Certificate('./serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'blacksheep-9a512.appspot.com'
})

# Get bucket object to upload/download files
bucket = storage.bucket()

# Enable CORS to allow requests from Frontend
app = Flask(__name__)
CORS(app)

# firestore client
db = firestore.client()

# generate salt for bcrypt
salt = bcrypt.gensalt(rounds=12)


def get_cipher(cipher, shape, key=None):
    if cipher == 'caesar':
        return Caesar(shape, key)
    elif cipher == 'modified_caesar':
        return ModifiedCaesar(shape, key)
    elif cipher == 'one_time_pad':
        return OneTimePad(shape, key)
    elif cipher == 'transposition':
        return Transposition(shape, key)


@app.route('/', methods=['GET'])
def index():
    return 'Pixelify backend API. Made using Flask and Python.', 200


@app.route('/ping', methods=['GET', 'POST'])
def ping():
    return 'pong!', 200


@app.route('/available-ciphers', methods=['GET'])
def cipher_list():
    return (
        jsonify(
            [
                {'display-name': 'Caesar\'s Cipher', 'api-name': 'caesar'},
                {'display-name': 'Modified Caesar\'s Cipher',
                    'api-name': 'modified_caesar'},
                {'display-name': 'One Time Pad', 'api-name': 'one_time_pad'},
                {'display-name': 'Transposition', 'api-name': 'transposition'}
            ]
        ),
        200,
    )


@app.route('/encrypt', methods=['POST'])
def encrypt():
    params = request.json
    password = params['password']
    image = params['image']
    cipher = params['cipher']

    # hash password using bcrypt
    password_bytes = str.encode(password)
    hash = bcrypt.hashpw(password_bytes, salt)

    # generate id, firestore doesn't support auto-increment id
    id = str(uuid.uuid4())

    # convert image to numpy array
    try:
        if 'image/png' in image:
            image = image[image.index(',') + 1:]
            base64_decoded = base64.b64decode(image)
            img = Image.open(BytesIO(base64_decoded))
        else:
            image = image[image.index(',') + 1:]
            base64_decoded = base64.b64decode(image)
            img = Image.open(BytesIO(base64_decoded)).convert('RGB')
    except:
        return 'Image format not supported', 415

    img = np.asarray(img)

    # create cipher object
    cipher_obj = get_cipher(cipher, img.shape)
    if cipher_obj is None:
        return 'Cipher not available', 400

    # encrypt
    cipher_obj.encrypt(img)

    # adding id to metadata
    data = pickle.dumps(id)
    exif_ifd = {piexif.ExifIFD.MakerNote: data}
    exif_dict = {'Exif': exif_ifd}
    exif_dat = piexif.dump(exif_dict)

    # convert encrypted image to base64
    image_format = 'PNG'
    image_head = 'data:image/png;base64,'
    pil_img = Image.fromarray(img)
    buff = BytesIO()
    try:
        pil_img.save(buff, format=image_format, exif=exif_dat)
        encrypted_image = base64.b64encode(buff.getvalue()).decode('utf-8')
    except:
        return 'Image format not supported', 415
    encrypted_image = image_head + encrypted_image

    # create a temp file to store cipher & key, with id.json as filename
    data = {}
    data['cipher'] = cipher
    data['key'] = cipher_obj.key

    file_name = f'{id}.json'
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

    # upload file to firebase storage
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)

    # delete temp file
    os.remove(file_name)

    # store hash and id in firestore
    doc_ref = db.collection('hash-id').document(id)
    doc_ref.set({'hash': hash, 'id': id})

    return encrypted_image, 200


@app.route('/decrypt', methods=['POST'])
def decrypt():
    params = request.json
    password = params['password']
    image = params['image']

    # convert image to numpy array
    try:
        if 'image/png' in image:
            image = image[image.index(',') + 1:]
            base64_decoded = base64.b64decode(image)
            img = Image.open(BytesIO(base64_decoded))
        else:
            image = image[image.index(',') + 1:]
            base64_decoded = base64.b64decode(image)
            img = Image.open(BytesIO(base64_decoded)).convert('RGB')
    except:
        return 'Image format not supported', 415

    img_mat = np.asarray(img)

    # extract id
    try:
        exif_dict = piexif.load(img.info['exif'])
        id = pickle.loads(exif_dict['Exif'][piexif.ExifIFD.MakerNote])
    except:
        return 'Image is not encrypted', 415

    # get password from firestore and verify
    doc_ref = db.collection('hash-id').where('id', '==', id).get()
    firestore_dict = doc_ref[0].to_dict()

    password_bytes = str.encode(password)
    if not bcrypt.checkpw(password_bytes, firestore_dict['hash']):
        return 'wrong password', 403

    # add .json to id and fetch file from firestore storage bucket
    file_name = f'{id}.json'
    blob = bucket.blob(file_name)
    blob.download_to_filename(file_name)

    # get cipher and key from file
    with open(file_name) as json_file:
        data = json.load(json_file)
        key = data['key']
        cipher = data['cipher']

    # delete file
    os.remove(file_name)

    # create cipher object
    cipher_obj = get_cipher(cipher, img_mat.shape, key)

    # decrypt image
    cipher_obj.decrypt(img_mat)

    # convert encrypted image to base64
    image_format = 'PNG'
    image_head = 'data:image/png;base64,'
    pil_img = Image.fromarray(img_mat)
    buff = BytesIO()
    try:
        pil_img.save(buff, format=image_format)
        decrypted_image = base64.b64encode(buff.getvalue()).decode('utf-8')
    except:
        return 'Image format not supported', 415
    decrypted_image = image_head + decrypted_image

    return decrypted_image, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
