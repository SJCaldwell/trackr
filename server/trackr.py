import os
import flask
import requests
from flask import current_app
from flask import redirect, url_for, request, session, Blueprint
from functools import wraps
from flask.ext.login import login_user, logout_user, current_user, LoginManager, login_required
from user import User
from oauth import OAuthSignIn
from flask import jsonify
from config.Config import DevelopmentConfig
from user import User
from hasher import hash_alg
from functools import wraps
from oauth import OAuthSignIn
from config.Config import DevelopmentConfig
from flask import redirect, url_for, request, session, Blueprint, jsonify, current_app
from flask.ext.login import login_user, logout_user, current_user, LoginManager, login_required
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask.ext.cors import CORS
import datetime, urllib, time, base64, time, hmac, json
from hashlib import sha1
from flask.ext.store import Store
from hough_track import Trackr

app = flask.Flask(__name__)
CORS(app, origins = "*api4trackr.herokuapp.com*")
app.config['STORE_DOMAIN'] = 'http://127.0.0.1:5000'
app.config['STORE_PATH'] = 'test/tracked/'
app.config['STORE_PROVIDER'] = 'flask_store.providers.s3.S3Provider'
app.config['STORE_S3_REGION'] = 'us-east-1'
app.config['STORE_S3_BUCKET'] = 'bartrackr-upload'
app.config['STORE_S3_ACCESS_KEY'] = os.environ.get("AWS_ACCESS_KEY_ID")
app.config['STORE_S3_SECRET_KEY'] = os.environ.get("AWS_SECRET_KEY")

store = Store(app)

app.config.from_object(DevelopmentConfig)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "barry_allen"
MONGO_URI = os.environ.get("MONGO_URI")

@login_manager.user_loader
def user_loader(user_id):
    user = User(user_id)
    return user

@app.route("/")
def index():
    return flask.render_template('index.html')

@app.route("/ajaxVideoUpload/<lift>/<weight>/", methods = ['POST', 'GET'])
@login_required
def uploadVideo(lift, weight):
    user = current_user
    user_id = user.user_id
    payload = {'user_id': user_id, 'lift_type': lift, 'weight': weight,
              'file_path': 'test', 'date': datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")}
    r = requests.post("http://api4trackr.herokuapp.com" + "/addLift",json = payload)
    file = request.files['file']
    upload_raw_video(file, user_id, lift, weight)
    if r.status_code != 200:
        return "IMPROPER"
    else:
        return r._content

def upload_raw_video(file, user_id, lift, weight):
    app.config['STORE_PATH'] = user_id + "/" + str(lift) + '/' + str(weight) + '/'
    provider = store.Provider(file)
    provider.save()
    print "SAVED COMPLETE"
    return provider.absolute_url

@app.route("/current_user/")
@login_required
def get_current_user():
    user = current_user
    if user:
        return jsonify({"status": "ok", "user": user.user_id})
    else:
        return jsonify({"status":"fail"})

@app.route('/logout_current_user/')
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'ok'})

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    oauth = OAuthSignIn.get_provider(provider)
    username, email = oauth.callback()
    print username
    print email
    print '\n GOT PAST CALLBACK'
    if email is None:
        return redirect(url_for('index'))
    nickname = username
    if nickname is None or nickname == "":
        nickname = email.split('@')[0]
        #url_for(post_user, username = nickname, password = password, email = email, provider = provider)
        return redirect(url_for('index'))
    else:
        #This is just a login
        user = user_loader(nickname)
        login_user(user)
        return redirect(url_for('index'))

'''
THE FOLLOWING ROUTES HAVE TO BE CHANGED TO BE SENT AJAX REQUESTS INSTEAD OF ARGUMENTS BEING SENT OVER HTTP
'''
@app.route('/api_post/<username>/<password>/<email>/', defaults = {'provider' : 'Trackr'}, methods = ['POST'])
def post_user(username, password, email, provider):
    print username
    payload = {'user_id': username, 'password': hash_alg(password), 'email': email, 'provider': provider}
    r = requests.post("https://api4trackr.herokuapp.com/Add", json= payload)
    if r.status_code != 200:
        return "Wrong format"
    return r._content

@app.route("/api_login/<username>/<password>", methods = ['POST'])
def get_user(username, password):
    payload = {'user_id': username, 'password': hash_alg(password)}
    r = requests.get("https://api4trackr.herokuapp.com/LoginUser", json = payload)
    if r.status_code != 200:
    	return "IMPROPER"
    r_json = r.json()
    if 'log_in' in r_json:
        user = r_json['log_in']
        user = user_loader(user)
        login_user(user)
        print "hello, " + str(current_user.user_id)
    return r._content

@app.route("/api_check/<username>/<email>")
def check_user(username, email):
    payload = {'user_id': username, "email" : email}
    r = requests.get("https://api4trackr.herokuapp.com" + "/Check", json = payload)
    if r.status_code != 200:
        return "IMPROPER"
    return r._content

@app.route("/api_get_lift/<username>")
def grab_lifts(username):
    payload = {'user_id': username}
    r = requests.get("https://api4trackr.herokuapp.com" + "/getLifts", json = payload)
    if r.status_code != 200:
        return "IMPROPER"
    return r._content


@app.route("/api_delete/<username>")
def delete_user(username):
    r = requests.get("https://api4trackr.herokuapp.com" + "/Delete")
    if r.status_code != 200:
        return "IMPROPER"
    return r._content

if __name__ == "__main__":
    app.run(debug = True)
