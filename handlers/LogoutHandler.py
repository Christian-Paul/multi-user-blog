import webapp2
import os
import jinja2
from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                               autoescape = True)

from models import Comment, Post, User
from BlogHandler import BlogHandler

class LogoutHandler(BlogHandler):
  def get(self):
    # clear username cookie
    self.response.headers.add_header('Set-Cookie', 'username=; Path="/"')
    self.redirect('/signup')