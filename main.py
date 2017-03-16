import os

import webapp2
import logging
import jinja2
import re
import time
import hmac
import random
import string
import hashlib
import json

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class User(db.Model):
  username = db.StringProperty(required = True) # TODO Don't allow duplicate username
  password = db.StringProperty(required = True)
  email = db.StringProperty()
  joined = db.DateTimeProperty(auto_now_add = True)
  # TODO add classmethod decorators to get by id
  # TODO add classmethod decorators to get by name

def get_all_users():
  return db.GqlQuery('SELECT * FROM User ')

def get_user_by_name(username):
  return db.GqlQuery('SELECT * FROM User WHERE username = :1', username).get()

class Post(db.Model):
  subject = db.StringProperty(required = True)
  content = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)
  author = db.ReferenceProperty(User)
  # TODO add classmethod decorators to get by id

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))

class BlogHandler(Handler):
  def read_secure_cookie(self, name):
    cookie_val = self.request.cookies.get(name)
    if cookie_val and check_secure_val(cookie_val):
      return cookie_val

  def set_secure_cookie(self, name, val):
    cookie_val = make_secure_val(val)
    self.response.headers.add_header(
                                     'Set-Cookie',
                                     '%s=%s' % (name, cookie_val))

  def initialize(self, *a, **kw):
    webapp2.RequestHandler.initialize(self, *a, **kw)

    self.authenticated = False
    self.user = None

    if self.read_secure_cookie('username'):
      un = self.read_secure_cookie('username').split('|')[0]

      # if first and second arguments are both true, set self.user to user object (second argument)
      self.user = un and get_user_by_name(un)

      if self.user:
        self.authenticated = True


class MainPage(BlogHandler):
  def get(self):
    posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')

    self.render('index.html', posts = posts, authenticated = self.authenticated, user = self.user)

class PostHandler(BlogHandler):
  def get(self, post_id):
    post = Post.get_by_id(int(post_id))

    if post:
      editing_target = self.request.get('editingTarget')
      self.render('post.html', post = post, authenticated = self.authenticated, editing_target = editing_target, user = self.user)
    else:
      self.error(404)

  def put(self, post_id):
    req_data = json.loads(self.request.body)

    p = Post.get_by_id(int(post_id))
    p.subject = req_data['subject']
    p.content = req_data['content']

    p.put()
    time.sleep(0.1)

    self.response.headers['Content-Type'] = 'text'
    self.write('Success!')

  def delete(self, post_id):
    # TODO validate that request is from user who owns this post
    # Post.get_by_id(int(post_id)).delete()
    # TODO bug: user was nonestype
    logging.info(self.user)
    username = None
    self.response.headers['Content-Type'] = 'text'
    if self.user:
      username = self.user.username
      logging.info(self.user.username)
      self.write('Success!')
    else:
      self.write('Deleted, user not found')


class NewPost(BlogHandler):
  def get(self):
    if not self.authenticated:
      self.redirect('/signup')

    self.render('new-post.html', authenticated = self.authenticated, user = self.user)

  def post(self):
    subject = self.request.get('subject')
    content = self.request.get('content')

    params = dict(subject = subject,
                  content = content, 
                  authenticated = self.authenticated)

    if subject and content and len(content) > 250 and self.authenticated:
      p = Post(subject = subject, content = content, author = self.user)
      p.put()
      post_id = str(p.key().id())

      time.sleep(0.1)

      self.redirect('/post/' + post_id)
    else:
      if len(content) <= 250:
        params['error_message'] = 'Post content must contain more than 250 characters'
      else:
        params['error_message'] = 'An error occurred'

      self.render('new-post.html', **params)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def validate_username(username):
  return username and USER_RE.match(username)

def check_original_username(username):
  if db.GqlQuery('SELECT * FROM User WHERE username = :1', username).count() == 0:
    return True

PASSWORD_RE = re.compile(r"^.{3,20}$")
def validate_password(password):
  return password and PASSWORD_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def validate_email(email):
  # returns true if there is no email, or if there is an email that passes the regex
  return not email or EMAIL_RE.match(email)

def make_salt():
    return string.join([random.choice(string.letters) for x in range(5)], '')

SECRET = 'DBB819D7DC166FC2FC45F4693F197'

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return str('%s|%s' % (s, hash_str(s)))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val

def make_pw_hash(name, pw, salt = make_salt()):
    hashed = hashlib.sha256(name + pw + salt).hexdigest()
    return hashed + ',' + salt

def valid_pw(name, pw, h):
    hash, salt = h.split(',')
    
    if make_pw_hash(name, pw, salt) == h:
        return True

class SignupHandler(BlogHandler):
  def get(self):
    if self.authenticated:
      self.redirect('/users/%s' % self.user.username)

    self.render('signup.html')

  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')
    verify = self.request.get('verify')
    email = self.request.get('email')

    params = dict(username = username,
                  email = email, 
                  authenticated = self.authenticated)

    valid_username = validate_username(username)
    original_username = check_original_username(username)
    valid_password = validate_password(password)
    valid_verify = password == verify
    valid_email = validate_email(email)

    if valid_username and original_username and valid_password and valid_verify and valid_email:
      # add user to database
      u = User(username = username, password = make_pw_hash(username, password), email = email)
      u.put()

      # TODO abstract setting cookies to a login function 
      self.response.headers.add_header('Set-Cookie', 'username=%s; Path="/"' % str(make_secure_val(username)))
      self.redirect('/welcome')

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

class LoginHandler(BlogHandler):
  def get(self):
    if self.authenticated:
      self.redirect('/users/%s' % self.user.username)

    self.render('login.html')

  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')

    # validate user
    user = get_user_by_name(username)
    if user:
      valid_password = valid_pw(username, password, user.password)

      # if successful, set cookie and redirect to welcome page
      if valid_password:
        self.response.headers.add_header('Set-Cookie', 'username=%s; Path="/"' % str(make_secure_val(username)))
        self.redirect('/welcome')

    # if fail, return to login page with error message
    error_message = 'Invalid username or password'
    self.render('login.html', username = username, error_message = error_message, authenticated = self.authenticated)

class WelcomeHandler(BlogHandler):
  def get(self):
    # validate cookie
    # TODO make function for checking cookies on every page
    username_cookie = self.request.cookies.get('username')
    if username_cookie and check_secure_val(username_cookie):
      username = username_cookie.split('|')[0]

      self.render('welcome.html', username = username, authenticated = self.authenticated, user = self.user)
    else:
      self.redirect('/')

class LogoutHandler(BlogHandler):
  def get(self):
    self.response.headers.add_header('Set-Cookie', 'username=; Path="/"')
    self.redirect('/signup')

class AllUsersHandler(BlogHandler):
  def get(self):
    users = get_all_users()
    self.render('user-index.html', users = users, authenticated = self.authenticated, user = self.user)

class UserHandler(BlogHandler):
  def get(self, username):
    user = get_user_by_name(username)

    if user:
      posts = user.post_set

      self.render('user.html', posts = posts, author = username, authenticated = self.authenticated, user = self.user)
    else:
      self.error(404)


app = webapp2.WSGIApplication([('/', MainPage), 
                              ('/newpost', NewPost),
                              ('/post/(\d+)', PostHandler),
                              ('/signup', SignupHandler),
                              ('/welcome', WelcomeHandler),
                              ('/login', LoginHandler),
                              ('/logout', LogoutHandler),
                              ('/users/', AllUsersHandler),
                              ('/users/(.+)', UserHandler)
                              ],
                              debug=True)