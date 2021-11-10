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
import uuid
import os

from api.caesar import Caesar

from cryptography.fernet import Fernet

# decrypt file using secret key
key = os.environ.get('PIXELIFY_KEY')
f = Fernet(key)

with open('./api/serviceAccountKey.enc', 'rb') as encrypted_file:
    encrypted = encrypted_file.read()

decrypted = f.decrypt(encrypted)
with open('./api/serviceAccountKey.json', 'wb') as decrypted_file:
    decrypted_file.write(decrypted)


# Use a service account
cred = credentials.Certificate('./api/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

app = Flask(__name__)


def get_cipher(cipher, size, key=None):
    if cipher == 'caesar':
        return Caesar(size, key)


@app.route('/', methods=['GET'])
def index():
    return 'Pixelify backend API. Made using Flask and Python.', 200


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong!', 200


@app.route('/encrypt', methods=['POST'])
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
    doc_ref = db.collection('hash-id').document(id)
    doc_ref.set({'hash': hash, 'id': id})

    # check if image is right format and storing image format
    if 'image/jpeg' in image:
        image_format = 'JPEG'
    elif 'image/png' in image:
        image_format = 'PNG'
    else:
        return 'Image format not supported', 415

    # convert image to numpy array
    image_head = image[:image.index(',')+1]
    image = image[image.index(',')+1:]
    base64_decoded = base64.b64decode(image)
    img = Image.open(BytesIO(base64_decoded))
    img = np.array(img)

    # create cipher object
    cipher_obj = get_cipher(cipher, img.size)

    # encrypt
    cipher_obj.encrypt(img)

    # adding id to metadata
    data = pickle.dumps(id)
    exif_ifd = {piexif.ExifIFD.MakerNote: data}
    exif_dict = {'Exif': exif_ifd}
    exif_dat = piexif.dump(exif_dict)

    # convert encrypted image to base64
    pil_img = Image.fromarray(img)
    buff = BytesIO()
    pil_img.save(buff, format=image_format, exif=exif_dat)
    encrypted_image = base64.b64encode(buff.getvalue()).decode('utf-8')
    encrypted_image = image_head+encrypted_image

    # store id, cipher and key in firestore
    doc_ref = db.collection('id-cipher-key').document(id)
    doc_ref.set(
        {
            'id': id,
            'cipher': cipher,
            'key': cipher_obj.key
        }
    )

    return encrypted_image, 200


@app.route('/decrypt', methods=['POST'])
def decrypt():
    params = request.json
    password = params['password']
    image = params['image']
    cipher = params['cipher']

    # check if image is right format and storing image format
    if 'image/jpeg' in image:
        image_format = 'JPEG'
    elif 'image/png' in image:
        image_format = 'PNG'
    else:
        return 'Image format not supported', 415

    # convert image
    image_head = image[:image.index(',')+1]
    image = image[image.index(',')+1:]
    base64_decoded = base64.b64decode(image)
    img = Image.open(BytesIO(base64_decoded))
    img_mat = np.array(img)

    # extract id
    exif_dict = piexif.load(img.info['exif'])
    id = pickle.loads(exif_dict['Exif'][piexif.ExifIFD.MakerNote])

    # get password from firestore and verify

    # get key from firestore
    key = 1

    # create cipher object
    cipher_obj = get_cipher(cipher, img_mat.size, key)

    # decrypt image
    cipher_obj.decrypt(img_mat)

    # convert encrypted image to base64
    pil_img = Image.fromarray(img_mat)
    buff = BytesIO()
    pil_img.save(buff, format=image_format)
    decrypted_image = base64.b64encode(buff.getvalue()).decode('utf-8')
    decrypted_image = image_head+decrypted_image

    return decrypted_image, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
