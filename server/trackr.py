import flask
from flask import redirect, url_for, request, session
import requests
from flask import Flask
from functools import wraps
from flask import Blueprint
from server.models import User
from authenticator import Authenticator

trackr_api = Blueprint('trackr_api', __name__)

#Decorator for logging in
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flask.flash('You need to login first.')
            return redirect(url_for('.login'))
    return wrap

@trackr_api.route("/")
def index():
	return flask.render_template('index.html')

@trackr_api.route("/secret")
@login_required
def secret():
	return flask.render_template('secret.html')

@trackr_api.route('/login', methods = ['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] == '' or request.form['password'] == '':
			error = "Please fill out the whole form"
		else:
			#try login
			print 'logging in is trying i think\n'
			authenticator = Authenticator(
				username = request.form['username'],
				password = request.form['password']
				)
			if authenticator.validLogin():
				session['logged_in'] = True 
				flask.flash('You were just logged in!')
				return redirect(url_for('.secret'))
			else:
				error = authenticator.error
				print 'trying to return login page ith error.'
				return flask.render_template('login.html', error = error)
	return flask.render_template('login.html', error = error)

@trackr_api.route('/register', methods = ['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if request.form['username'] == '' or request.form['password'] == '' or request.form['email'] == '':
			error = "Please fill out the whole form"
		else:
			authenticator = Authenticator(
				username = request.form['username'],
				password = request.form['password'],
				email = request.form['email']
			)
			if authenticator.validForm():
				user = User(
					username = validator.username,
					password = validator.password,
					email = validator.email
					)
				user.save()
				flask.flash('You were just registered! Use these credentials to login!')
				return redirect(url_for('.login'))
			else:
				error = authenticator.error
	return flask.render_template('register.html', error = error)

@trackr_api.route('/logout')
@login_required
def logout():
	session.pop('logged_in', None)
	flask.flash("You were just logged out!")
	return redirect(url_for('.index'))

@trackr_api.route("/api_test")
def create_task():
    r = requests.get("http://127.0.0.1:8000/User")
    if r.status_code != 200:
        return
    return r._content

@trackr_api.route("/fuck")
def fuck():
	return redirect(url_for('index'))