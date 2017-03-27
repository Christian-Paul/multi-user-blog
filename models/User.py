from google.appengine.ext import db

class User(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.StringProperty()
	joined = db.DateTimeProperty(auto_now_add = True)

	@classmethod
	def by_name(cls, username):
		return db.GqlQuery('SELECT * FROM User WHERE username = :1', username).get()

	@classmethod
	def get_all(cls):
		return db.GqlQuery('SELECT * FROM User ')

	@classmethod
	def check_original_username(cls, username):
		if db.GqlQuery('SELECT * FROM User WHERE '
		'username = :1', username).count() == 0:
			return True