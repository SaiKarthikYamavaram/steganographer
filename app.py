from flask import Flask, render_template, url_for, request, send_file
from flask import *
import os

from cryptography.fernet import Fernet
import helper
from helper.steganography import *
app = Flask(__name__, instance_path='D:\\mini-project\\flask\\steganographer\\decryption_input')
app.config['CLIENT_IMG']= "D:\mini-project\\flask\steganographer\encrypted_output"

def TxtDecrypt(data, key):
    # print(data)
    # data = str.decode(data)
    f = Fernet(key)
    decrypted = f.decrypt(data)
    return decrypted


def TxtEncrypt(data, key):
    data_encoded = data.encode()  # Converting message string to utf-8 format
    fObject = Fernet(key)  # a Fernet object
    data1 = fObject.encrypt(data_encoded)
    return data1


@app.route('/get-img')
def get_image():
    photo = "upload\download.png"
    return send_file(photo, mimetype="image/png")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/encryption')
def encryption():
    return render_template('encryption.html')


@app.route('/decryption')
def decryption():
    return render_template('decryption.html')


@app.route('/upload_encryption', methods=["GET", "POST"])
def on_upload():
    if(request.method == "POST"):
        file = open('key.key', 'rb')  # Open the file as wb to read bytes
        key = file.read()  # The key will be type bytes
        file.close()
        print(request.form['encryption-data'],
              type(request.form['encryption-data']))
        decrypted_text = TxtEncrypt(request.form['encryption-data'], key)
        hide_data_to_image(decrypted_text)
        return send_from_directory(app.config["CLIENT_IMG"], filename="_with_hidden_file.png", as_attachment=True)


    else:
        return render_template('error.html')


@app.route('/upload_decryption', methods=["GET", "POST"])
def on_upload_decryption():
    if(request.method == "POST"):
        file = open('key.key', 'rb')  # Open the file as wb to read bytes
        key = file.read()  # The key will be type bytes
        file.close()
        f = request.files["decryption-file"]
        img_loc = os.path.join(app.instance_path, f.filename)
        f.save(img_loc)
        encrypted_text = extract_message_from_image(img_loc)
        # print(type(request.form['decryption-data']),type(encrypted_text))
        decrypted_text = TxtDecrypt(encrypted_text, key)
        return decrypted_text

    else:
        return render_template('error.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html')


@app.route('/team')
def team():
    return 'about us'


if __name__ == '__main__':
    app.run(debug=True)
