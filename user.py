from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class User(object):

    def __init__(self, username, password, author):
        self.username = username
        self.set_password(password)
        self.link_karma = 0
        self.comment_karma = 0
        self.created = datetime.datetime.utcnow()

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    #saves into mongo.db
    def push