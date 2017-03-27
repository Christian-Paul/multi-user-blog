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

class PostHandler(BlogHandler):
  def get(self, post_id):
    # get post by id, and its comments, sorted by recent
    post = Post.get_by_id(int(post_id))
    comments = db.GqlQuery('SELECT * FROM Comment WHERE post = :1 '
                           'ORDER BY created DESC', post)

    if post:
      # editing target is set to post 
      # to let template know to render editing view
      # only allow this if current user is author of this post
      if post.author.username == (self.user and self.user.username):
        editing_target = self.request.get('editingTarget')
      else:
        editing_target = None

      if self.user:
        user_key = self.user.key()
      else:
        user_key = None

      self.render('post.html', post = post, authenticated = self.authenticated,
                  editing_target = editing_target, user = self.user,
                  user_key = user_key, comments = comments)
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
      time.sleep(0.1)
      self.write(self.user.username)
    else:
      self.write('error')