import webapp2
import os
import jinja2
from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                               autoescape = True)

from models import Comment, Post, User
from BlogHandler import BlogHandler

class MainPageHandler(BlogHandler):
  def get(self):
    # send posts, sorted by recent
    posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')
    self.render('index.html', posts = posts, 
                authenticated = self.authenticated, user = self.user)