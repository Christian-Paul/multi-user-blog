import webapp2
import os
import jinja2
import hmac
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                               autoescape = True)

from models import Comment, Post, User
from Handler import Handler

SECRET = 'DBB819D7DC166FC2FC45F4693F197'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()


def make_secure_val(s):
    return str('%s|%s' % (s, hash_str(s)))


def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val


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

      # if first and second arguments are both true, 
      # set self.user to user object (second argument)
      self.user = un and User.by_name(un)

      if self.user:
        self.authenticated = True