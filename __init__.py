from datetime import datetime

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
from bson.son import SON
from werkzeug.security import generate_password_hash, check_password_hash

import utils
import models
import config as config


app = Flask(__name__)
app.config.from_object(config)
mongo = PyMongo(app)


@app.route('/')
def home():
	posts = mongo.db.posts.find()
	posts.sort('score', -1)
	#update session account
	if session.get('logged_in'):
		session['account'] = update_session_account()
	return render_template('show_posts.html', posts=posts)

@app.route('/flush')
def flush():
	if session.get('logged_in'):
		redirect(url_for('logout'))
	mongo.db.posts.remove()
	mongo.db.accounts.remove()
	return redirect(url_for('home'))

## POST ######

@app.route('/add', methods=['POST'])
def add_post():
	if not session.get('logged_in'):
		flash("You must be logged in to post links.")
		return redirect(url_for('new_post'))

	if utils.valid_link(request.form['link']):
		post = models.Post(request.form['title'], request.form['link'], session['account'])
		mongo.db.posts.insert(post)
		return redirect(url_for('home'))
	else:
		flash("Please begin link with \"http(s)://\"")
		return redirect(url_for('new_post'))

@app.route('/new', methods=['GET'])
def new_post():
	return render_template('new_post.html')


@app.route('/post/<post_id>')
def view_post(post_id):
	post_id = ObjectId(post_id)
	p = mongo.db.posts.find_one({'_id': post_id})
	return render_template('show_post.html', p=p)


## UPVOTE/DOWNVOTE ###########################################


@app.route('/post/<post_id>/up', methods= ['POST'])
def upvote(post_id):
	if already_scored(post_id) == 1:
		flash('You may not upvote twice')

	elif already_scored(post_id) == -1:
		#upvote twice to remove the initial downvote
		update_post_score(post_id, 1)
		update_post_score(post_id, 1)
	else:
		update_post_score(post_id, 1)

	return redirect(url_for('home'))

@app.route('/post/<post_id>/down', methods= ['POST'])
def downvote(post_id):
	if already_scored(post_id) == -1:
		flash('You may not downvote twice')

	elif already_scored(post_id) == 1:
		#downvote twice to remove the initial upvote
		update_post_score(post_id, -1)
		update_post_score(post_id, -1)

	else:
		update_post_score(post_id, -1)

	return redirect(url_for('home'))

def update_post_score(post_id, amount):
	update_session_account()
	#change post score
	mongo.db.posts.update({'_id': ObjectId(post_id)}, {"$inc": {"score": amount}})
	author = get_post_author(post_id)
	scorer = session['account']['_id']
	#change user info
	mongo.db.accounts.update({'username': author['username']}, {'$inc': {"link_karma": amount}})
	mongo.db.accounts.update({'_id': scorer}, {'$set': {'scored.%s' % post_id: amount}})
	return

def get_post_author(post_id):
	return mongo.db.posts.find_one({'_id': ObjectId(post_id)})['author']

def already_scored(post_id):
	return session['account']['scored'].get(post_id)


## LOGIN/LOGOUT ###################################

@app.route('/register', methods= ['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('register.html')

	username = request.form['username']
	password = request.form['password']

	if not (utils.valid_username(username) and utils.valid_password(password)):
		flash("Please use only a username of only letters and/or numbers between 3 and 20 characters")
		return render_template('register.html')

	if username_taken(username):
		flash("username is already taken, please try another")
		return render_template('register.html')

	else:	
		add_user(username, password)
		#flash("user registered successfully")
		login_session(username)
		return redirect(url_for('home'))

@app.route('/login', methods= ['GET', 'POST'])
def login():
	if session.get('logged_in'):
		flash("You're already logged in.")
		return redirect(url_for('home'))

	if request.method == 'GET':
		return render_template('login.html')

	username = request.form['username']
	password = request.form['password']

	if not username_taken(username):
		flash('Username not found')
		return render_template('login.html')

	pw_hash = mongo.db.accounts.find_one({'username': username})['pw_hash']

	if not check_password_hash(pw_hash, password):
		flash('Password does not match user')
		return render_template('login.html')

	else:
		return login_session(username)

@app.route('/logout')
def logout():
	if session.get('logged_in'):
		session['logged_in'] = False
		#flash('Successfully logged out.')
		return redirect(url_for('home'))

	else:
		flash('You are not logged in.')
		return redirect(url_for('home'))

def login_session(username):
	session['account'] = mongo.db.accounts.find_one({'username': username})
	session['logged_in'] = True
	#flash('Logged in as %s' % username)
	return redirect(url_for('home'))

## USERS ######################################

def add_user(username, password):
	new_user = models.Account(username, generate_password_hash(password))
	return mongo.db.accounts.insert(new_user)

def username_taken(username):
	for acct in mongo.db.accounts.find():
		if username == acct['username']:
			return True
	return False

@app.route('/users', methods= ['GET'])
def show_users():
	accts = mongo.db.accounts.find()
	accts.sort('link_karma', -1)
	return render_template('show_users.html', accts = accts)

@app.route('/users/<username>')
def show_user(username):
	acct = mongo.db.accounts.find({'username': username})
	return render_template('show_users.html', accts = acct)

def update_session_account():
	return mongo.db.accounts.find_one({'_id': session['account']['_id']})




# COMMENTS ####################################


@app.route('/post/<post_id>/comments', methods= ['POST'])
def comment(post_id):
	if (session.get('logged_in')):
		author = session['account']
		comment = models.Comment(request.form['comment'], author)
		mongo.db.posts.update({'_id': ObjectId(post_id)}, {'$push': {'comments': comment}}) 
	return redirect(url_for('view_post', post_id=post_id))

