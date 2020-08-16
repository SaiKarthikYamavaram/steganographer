from flask import Flask, render_template, url_for, request, send_file
from flask import *
import os
from cryptography.fernet import Fernet

import helper
from helper.steganography import *


app = Flask(
    __name__, instance_path='C:\\Users\\ysaik\\Desktop\\New folder (3)\\steganographer\\decryption_input')
app.config['CLIENT_IMG'] = "C:\\Users\\ysaik\\Desktop\\New folder (3)\\steganographer\\encrypted_output"


def TxtDecrypt(data, key):
    # print(data)
    # data = str.decode(data)
    try:
        f = Fernet(key)
        decrypted = f.decrypt(data)
        return decrypted
    except:
        return False


def TxtEncrypt(data, key):
    # Converting message string to utf-8 format i.e ascii binary
    data_encoded = data.encode()
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
        if(encrypted_text == False):
            return render_template('decryption.html', Error="There Seems to be some Error")

        decrypted_text = TxtDecrypt(encrypted_text, key)
        if(decrypted_text == False):
            return render_template('decryption.html', Error="There Seems to be some Error or The Image File is Corrupted")

        return render_template('result_encryption.html', result=decrypted_text.decode('ascii'))

    else:
        return render_template('error.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html')


@app.route('/about')
def team():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
