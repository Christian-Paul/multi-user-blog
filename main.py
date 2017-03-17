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
  username = db.StringProperty(required = True)
  password = db.StringProperty(required = True)
  email = db.StringProperty()
  joined = db.DateTimeProperty(auto_now_add = True)

def get_all_users():
  return db.GqlQuery('SELECT * FROM User ')

def get_user_by_name(username):
  return db.GqlQuery('SELECT * FROM User WHERE username = :1', username).get()

class Post(db.Model):
  subject = db.StringProperty(required = True)
  content = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)
  author = db.ReferenceProperty(User)
  likes = db.ListProperty(db.Key)

class Comment(db.Model):
  author = db.ReferenceProperty(User)
  post = db.ReferenceProperty(Post)
  content = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)

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
    # on every request, read cookies and set user data if valid
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
    # send posts, sorted by recent
    posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')
    self.render('index.html', posts = posts, authenticated = self.authenticated, user = self.user)

class SignupHandler(BlogHandler):
  def get(self):
    # if authenticated, redirect to user's page, else render signup page
    if self.authenticated:
      self.redirect('/users/%s' % self.user.username)

    self.render('signup.html')

  def post(self):
    # if all fields are valid and username is unique, add user to database and set cookies
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
      u = User(username = username, password = make_pw_hash(username, password), email = email)
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
    user = get_user_by_name(username)
    if user:
      # validate passwords match
      valid_password = valid_pw(username, password, user.password)

      if valid_password:
        self.set_secure_cookie('username', username)
        self.redirect('/')

    # if fail, return to login page with error message
    error_message = 'Invalid username or password'
    self.render('login.html', username = username, error_message = error_message, authenticated = self.authenticated)

class LogoutHandler(BlogHandler):
  def get(self):
    # clear username cookie
    self.response.headers.add_header('Set-Cookie', 'username=; Path="/"')
    self.redirect('/signup')

class AllUsersHandler(BlogHandler):
  def get(self):
    # return all users
    users = get_all_users()
    self.render('user-index.html', users = users, authenticated = self.authenticated, user = self.user)

class UserHandler(BlogHandler):
  def get(self, username):
    # return all of a user's posts
    user = get_user_by_name(username)

    if user:
      posts = user.post_set
      self.render('user.html', posts = posts, author = username, authenticated = self.authenticated, user = self.user)
    else:
      self.error(404)

class PostHandler(BlogHandler):
  def get(self, post_id):
    # get post by id, and its comments, sorted by recent
    post = Post.get_by_id(int(post_id))
    comments = db.GqlQuery('SELECT * FROM Comment WHERE post = :1 ORDER BY created DESC', post)

    if post:
      # editing target is set to post to let template know to render editing view
      # only allow this if current user is author of this post
      if post.author.username == (self.user and self.user.username):
        editing_target = self.request.get('editingTarget')
      else:
        editing_target = None

      if self.user:
        user_key = self.user.key()
      else:
        user_key = None

      self.render('post.html', post = post, authenticated = self.authenticated, editing_target = editing_target, user = self.user, user_key = user_key, comments = comments)
    else:
      self.error(404)

  def put(self, post_id):
    # update post with new data
    # only allow if current user is author of this post
    self.response.headers['Content-Type'] = 'text'
    req_data = json.loads(self.request.body)

    p = Post.get_by_id(int(post_id))

    if p.author.username == (self.user and self.user.username):
      p.subject = req_data['subject']
      p.content = req_data['content']
      p.put()
      time.sleep(0.1)

      self.write('ok')
    else:
      self.write('error')


  def delete(self, post_id):
    # delete post
    # only allow if current user is author of this post
    self.response.headers['Content-Type'] = 'text'

    p = Post.get_by_id(int(post_id))
    if p.author.username == (self.user and self.user.username):
      p.delete()
      self.write('ok')
    else:
      self.write('error')


class NewPostHandler(BlogHandler):
  def get(self):
    # if authenticated, render new post page, otherwise redirect to signup
    if not self.authenticated:
      self.redirect('/signup')

    self.render('new-post.html', authenticated = self.authenticated, user = self.user)

  def post(self):
    # submit new post
    # only allow if authenticated
    if not self.authenticated:
      self.response.headers['Content-Type'] = 'text'
      self.write('error')

    else:
      subject = self.request.get('subject')
      content = self.request.get('content')

      params = dict(subject = subject,
                    content = content, 
                    authenticated = self.authenticated,
                    user = self.user)

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

class LikePostHandler(BlogHandler):
  def put(self, post_id):
    # toggle whether or not the current user likes a post
    # only allow authenticated users to like/unlike posts
    self.response.headers['Content-Type'] = 'text'
    if not self.authenticated:
      self.write('error')
    else:
      p = Post.get_by_id(int(post_id))
      user_key = self.user.key()

      if user_key in p.likes:
        p.likes.remove(user_key)
      else:
        p.likes.append(user_key)

      p.put()
      time.sleep(0.1)
      self.write('ok')

class NewCommentHandler(BlogHandler):
  def post(self, post_id):
    # post a new comment
    # only allow authenticated users to access
    if not self.authenticated:
      self.response.headers['Content-Type'] = 'text'
      self.write('error')

    else:
      content = self.request.get('content')
      post = Post.get_by_id(int(post_id))
      user = self.user
      c = Comment(author = user, post = post, content = content)

      c.put()
      time.sleep(0.1)

      self.redirect('/post/%s' % post_id)

class CommentHandler(BlogHandler):
  def delete(self, post_id, comment_id):
    # delete a comment
    # only allow author to delete comment
    self.response.headers['Content-Type'] = 'text'
    c = Comment.get_by_id(int(comment_id))

    if c.author.username == (self.user and self.user.username):
      c.delete()
      self.write('ok')
    else:
      self.write('error')

  def put(self, post_id, comment_id):
    # update a comment
    # only allow author to update comment
    req_data = json.loads(self.request.body)
    c = Comment.get_by_id(int(comment_id))

    if c.author.username == (self.user and self.user.username):
      c.content = req_data['content']
      c.put()
      time.sleep(0.1)

      self.write('ok')
    else:
      self.write('error')

app = webapp2.WSGIApplication([('/', MainPage), 
                              ('/newpost', NewPostHandler),
                              ('/post/(\d+)', PostHandler),
                              ('/post/(\d+)/like', LikePostHandler),
                              ('/signup', SignupHandler),
                              ('/login', LoginHandler),
                              ('/logout', LogoutHandler),
                              ('/users/', AllUsersHandler),
                              ('/users/(.+)', UserHandler),
                              ('/post/(\d+)/comment', NewCommentHandler),
                              ('/post/(\d+)/comment/(\d+)', CommentHandler)
                              ],
                              debug=True)