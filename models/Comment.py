from google.appengine.ext import db
from User import User
from Post import Post

class Comment(db.Model):
  author = db.ReferenceProperty(User)
  post = db.ReferenceProperty(Post)
  content = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)