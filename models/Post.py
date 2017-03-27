from google.appengine.ext import db
from User import User

class Post(db.Model):
  subject = db.StringProperty(required = True)
  content = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)
  author = db.ReferenceProperty(User)
  likes = db.ListProperty(db.Key)