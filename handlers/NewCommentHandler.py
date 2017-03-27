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