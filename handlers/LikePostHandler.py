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

class LikePostHandler(BlogHandler):
  def put(self, post_id):
    # toggle whether or not the current user likes a post
    # only allow authenticated users to like/unlike posts
    # don't allow authors to like their own posts
    self.response.headers['Content-Type'] = 'text'
    if not self.authenticated:
      self.write('error')
    else:
      p = Post.get_by_id(int(post_id))

      # make sure post exists
      if not p:
        self.write('error')
      else:
        # make sure user is not the author of the post
        user_key = self.user.key()
        if p.author.username == (self.user and self.user.username):
          self.write('error')

        else:
          # toggle whether the user likes the post
          if user_key in p.likes:
            p.likes.remove(user_key)
          else:
            p.likes.append(user_key)

          p.put()
          time.sleep(0.1)
          self.write('ok')