import datetime

def Post(title, link, author, score=0):
	return {"title": title,
			"link": link,
			"author": author,
			"score": score,
			"created": datetime.datetime.utcnow(),
			"comments": []
			}

def Account(user, pw_hash, link_karma=0, comment_karma=0):
	return {'username': user,
			'pw_hash': pw_hash,
			'link_karma': 0,
			'comment_karma': 0,
			'created': datetime.datetime.utcnow(),
			'scored': {},
			}

def Comment(text, author, score=0):
	return {
			'text': text,
			'author': author,
			'score': score,
			'created': datetime.datetime.utcnow(),
			'scored': {},
			'children': []
			}