from flask import session, redirect, url_for, request
from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId

from zfeed import app
from models import Comment

@app.route('/post/<post_id>/comments', methods= ['POST'])
def comment(post_id):
	if (session.get('logged_in')):
		author = session['account']
		comment = Comment(request.form['comment'], author)
		mongo.db.posts.update({'_id': ObjectId(post_id)}, {'$push': {'comments': comment}}) 
	return redirect(url_for('view_post', post_id=post_id))

