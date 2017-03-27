import webapp2
import os
import jinja2
import random
import string
import hashlib
from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                               autoescape = True)

from models import Comment, Post, User
from BlogHandler import BlogHandler


def make_salt():
    return string.join([random.choice(string.letters) for x in range(5)], '')


def make_pw_hash(name, pw, salt = make_salt()):
    hashed = hashlib.sha256(name + pw + salt).hexdigest()
    return hashed + ',' + salt


def valid_pw(name, pw, h):
    hash, salt = h.split(',')
    
    if make_pw_hash(name, pw, salt) == h:
        return True
        

class LoginHandler(BlogHandler):
  def get(self):
    # if authenticated, redirect to user's page, else render login page
    if self.authenticated:
      self.redirect('/users/%s' % self.user.username)

    self.render('login.html')

  def post(self):
    # if user credentials match, set cookies
    username = self.request.get('username')
    password = self.request.get('password')

    # validate user exists
    user = User.by_name(username)
    if user:
      # validate passwords match
      valid_password = valid_pw(username, password, user.password)

      if valid_password:
        self.set_secure_cookie('username', username)
        self.redirect('/')

    # if fail, return to login page with error message
    error_message = 'Invalid username or password'
    self.render('login.html', username = username, 
                error_message = error_message, 
                authenticated = self.authenticated)