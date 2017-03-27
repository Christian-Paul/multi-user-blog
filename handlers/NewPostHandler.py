import webapp2
import os
import jinja2
import time
from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                               autoescape = True)

from models import Comment, Post, User
from BlogHandler import BlogHandler

class NewPostHandler(BlogHandler):
  def get(self):
    # if authenticated, render new post page, otherwise redirect to signup
    if not self.authenticated:
      self.redirect('/signup')

    self.render('new-post.html', authenticated = self.authenticated, 
                user = self.user)

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
          params['error_message'] = ('Post content must contain '
                                     'more than 250 characters')
        else:
          params['error_message'] = 'An error occurred'

        self.render('new-post.html', **params)