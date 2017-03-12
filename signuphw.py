import os

import webapp2
import logging
import jinja2
import re

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))

class MainPage(Handler):
  def get(self):
    items = self.request.get_all('food')
    self.render('shopping_list.html', items = items)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def validate_username(username):
  return username and USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}$")
def validate_password(password):
  return password and PASSWORD_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def validate_email(email):
  # returns true if there is no email, or if there is an email that passes the regex
  return not email or EMAIL_RE.match(email)

class SignupHandler(Handler):
  def get(self):
    self.render('signup.html')

  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')
    verify = self.request.get('verify')
    email = self.request.get('email')

    params = dict(username = username,
                  email = email)

    valid_username = validate_username(username)
    valid_password = validate_password(password)
    valid_verify = password == verify
    valid_email = validate_email(email)

    if valid_username and valid_password and valid_verify and valid_email:
      self.response.headers.add_header('Set-Cookie', 'username=%s; Path="/"' % str(username))
      self.redirect('/welcome')

    else:
      if not valid_username:
        params['username_error'] = 'Invalid username'

      if not valid_password:
        params['password_error'] = 'Invalid password'

      elif not valid_verify:
        params['verify_error'] = 'Passwords do not match'

      if not valid_email:
        params['email_error'] = 'Invalid email'

      self.render('signup.html', **params)

class WelcomeHandler(Handler):
  def get(self):
    self.render('welcome.html', username=self.request.cookies.get('username'))


app = webapp2.WSGIApplication([('/', MainPage), ('/signup', SignupHandler), ('/welcome', WelcomeHandler)],
                              debug=True)