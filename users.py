from flask import render_template, Blueprint

from zfeed import app, mongo

users_blueprint = Blueprint('users', __name__)

@app.route('/users', methods= ['GET'])
def show_users():
	accts = mongo.db.accounts.find()
	accts.sort('link_karma', -1)
	return render_template('show_users.html', accts = accts)

@app.route('/users/<username>')
def show_user(username):
	acct = mongo.db.accounts.find({'username': username})
	return render_template('show_users.html', accts = acct)
