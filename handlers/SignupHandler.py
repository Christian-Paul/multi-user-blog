import webapp2
import os
import jinja2
import re
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


PASSWORD_RE = re.compile(r"^.{3,20}$")
def validate_password(password):
  return password and PASSWORD_RE.match(password)


EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def validate_email(email):
  # returns true if there is no email, 
  # or if there is an email that passes the regex
  return not email or EMAIL_RE.match(email)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def validate_username(username):
  return username and USER_RE.match(username)


class SignupHandler(BlogHandler):
  def get(self):
    # if authenticated, redirect to user's page, else render signup page
    if self.authenticated:
      self.redirect('/users/%s' % self.user.username)

    self.render('signup.html')

  def post(self):
    # if all fields are valid and username is unique, 
    # add user to database and set cookies
    username = self.request.get('username')
    password = self.request.get('password')
    verify = self.request.get('verify')
    email = self.request.get('email')

    params = dict(username = username,
                  email = email, 
                  authenticated = self.authenticated)

    valid_username = validate_username(username)
    original_username = User.check_original_username(username)
    valid_password = validate_password(password)
    valid_verify = password == verify
    valid_email = validate_email(email)

    if (valid_username and original_username and valid_password 
        and valid_verify and valid_email):
      u = User(username = username, password = 
               make_pw_hash(username, password), email = email)
      u.put()

      self.set_secure_cookie('username', username)
      self.redirect('/')

    else:
      if not valid_username:
        params['username_error'] = 'Invalid username'

      if not original_username:
        params['username_error'] = 'Username already taken'

      if not valid_password:
        params['password_error'] = 'Invalid password'

      elif not valid_verify:
        params['verify_error'] = 'Passwords do not match'

      if not valid_email:
        params['email_error'] = 'Invalid email'

      self.render('signup.html', **params)