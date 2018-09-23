import webapp2
from module.movies.Handler import BaseHandler
from module.movies.Handler import ViewHandler
from module.movies.Handler import HomeHandler
from module.movies.Handler import HandlerWithError
from module.movies.Handler import ImportHandler


app = webapp2.WSGIApplication([
    webapp2.Route('/', HomeHandler, name='home'),
    webapp2.Route('/view/<url>', ViewHandler, name='view'),
    webapp2.Route('/exception', HandlerWithError),
    webapp2.Route('/import', ImportHandler)
])