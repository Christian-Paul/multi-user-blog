import webapp2
import handlers


app = webapp2.WSGIApplication([('/', handlers.MainPageHandler), 
                              ('/newpost', handlers.NewPostHandler),
                              ('/post/(\d+)', handlers.PostHandler),
                              ('/post/(\d+)/like', handlers.LikePostHandler),
                              ('/signup', handlers.SignupHandler),
                              ('/login', handlers.LoginHandler),
                              ('/logout', handlers.LogoutHandler),
                              ('/users/', handlers.AllUsersHandler),
                              ('/users/(.+)', handlers.UserHandler),
                              ('/post/(\d+)/comment', handlers.NewCommentHandler),
                              ('/post/(\d+)/comment/(\d+)', handlers.CommentHandler)
                              ],
                              debug=True)