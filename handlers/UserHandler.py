import webapp2
import os
import jinja2
from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                               autoescape = True)

from models import Comment, Post, User
from BlogHandler import BlogHandler

class UserHandler(BlogHandler):
  def get(self, username):
    # return all of a user's posts
    user = User.by_name(username)

    if user:
      posts = db.GqlQuery('SELECT * FROM Post WHERE author = :1 '
                          'ORDER BY created DESC', user)
      self.render('user.html', posts = posts, author = username, 
                  authenticated = self.authenticated, user = self.user)
    else:
      self.error(404)