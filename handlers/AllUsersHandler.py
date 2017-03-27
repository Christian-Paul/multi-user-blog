import webapp2
import os
import jinja2
from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                               autoescape = True)

from models import Comment, Post, User
from BlogHandler import BlogHandler

class AllUsersHandler(BlogHandler):
  def get(self):
    # return all users
    users = User.get_all()
    self.render('user-index.html', users = users, 
                authenticated = self.authenticated, user = self.user)