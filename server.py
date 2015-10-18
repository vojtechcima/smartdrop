from flask import Flask
from flask import request
from flask import send_from_directory, send_file
from flask.ext.httpauth import HTTPBasicAuth
from os import remove
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
from io import BytesIO

auth = HTTPBasicAuth()

UPLOAD_FOLDER = '/tmp/'
ENCRYPTION_KEY = 'my_encryption_key'

# Models
UPLOADED = []
USERS = {}
USERS['admin'] = 'pbkdf2:sha1:1000$njxjP9FM$598155da4d6fb6a99f3c658fb44f495b51f120a7'


app = Flask(__name__)

@auth.verify_password
def verify_password(username, password):
    if USERS.get(username):
        if check_password_hash(USERS[username], password):
            return True
    return False

@app.route('/', methods=['POST', 'GET'])
@auth.login_required
def upload():
    if request.method == 'POST':
        for k in request.files.keys():
            f_in = request.files[k]
            f_out = open('%s%s' % (UPLOAD_FOLDER, k), 'wb')
            encrypt(f_in, f_out, ENCRYPTION_KEY)
            if k not in UPLOADED:
                UPLOADED.append(k)
    elif request.method == 'GET':
        return str(UPLOADED)
    return "Uploaded!"

@app.route('/<path:filename>', methods=['GET', 'DELETE'])
@auth.login_required
def download(filename):
    if request.method == 'GET':
        f_in = open('%s%s' % (UPLOAD_FOLDER, filename), 'rb')
        print f_in
        f_out = BytesIO()
        decrypt(f_in, f_out, ENCRYPTION_KEY)
        f_out.seek(0)
        return send_file(f_out,
                         attachment_filename=filename,
                         as_attachment=True)
    elif request.method == 'DELETE':
        remove('%s%s' % (UPLOAD_FOLDER, filename))
        UPLOADED.remove(filename)
        return 'Removed!'


def derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = ''
    while len(d) < key_length + iv_length:
        d_i = md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length+iv_length]

def encrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size
    salt = Random.new().read(bs - len('Salted__'))
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    out_file.write('Salted__' + salt)
    finished = False
    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += padding_length * chr(padding_length)
            finished = True
        out_file.write(cipher.encrypt(chunk))

def decrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size
    salt = in_file.read(bs)[len('Salted__'):]
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(chunk[-1])
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(chunk)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6664, debug=True)
