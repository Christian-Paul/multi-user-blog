import webapp2
import os
import jinja2
import time
import json
from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                               autoescape = True)

from models import Comment, Post, User
from BlogHandler import BlogHandler

class CommentHandler(BlogHandler):
  def delete(self, post_id, comment_id):
    # delete a comment
    # only allow author to delete comment
    self.response.headers['Content-Type'] = 'text'
    c = Comment.get_by_id(int(comment_id))

    # make sure comment exists
    if not c:
      self.write('error')
    else:
      # make sure user is the author of the comment
      if c.author.username != (self.user and self.user.username):
        self.write('error')
      else:
        c.delete()
        time.sleep(0.1)
        self.write('ok')

  def put(self, post_id, comment_id):
    # update a comment
    # only allow author to update comment
    req_data = json.loads(self.request.body)
    c = Comment.get_by_id(int(comment_id))

    # make sure comment exists
    if not c:
      self.write('error')

    else:
      # make sure user is the author of the comment
      if c.author.username != (self.user and self.user.username):
        self.write('error')
      else:
        c.content = req_data['content']
        c.put()
        time.sleep(0.1)

        self.write('ok')