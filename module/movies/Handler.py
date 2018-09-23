import webapp2
from webapp2_extras import jinja2
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from module.ndb.Db import MoviesDb
import urllib2
import json

class BaseHandler(webapp2.RequestHandler):

    ITEM_PER_PAGE = 100;
    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        self.jinja2.default_config = {'template_path': 'templates', 'force_compiled': False, 'globals': None, 'filters': None, 'environment_args': {'autoescape': True, 'extensions': ['jinja2.ext.autoescape', 'jinja2.ext.with_']}, 'compiled_path': None}
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)


class HomeHandler(BaseHandler):
    def get(self):
        context = {'message': 'Hello, world!'}
        self.render_response('home.html', **context)




class ViewHandler(BaseHandler):
    ITEM_PER_PAGE = 30;
    #This approch is not currect but for now i am using for demo app. for prodcution with should go with individual view to make  maintainable project
    def get(self, **kwargs):
        url = kwargs.get('url')
        allows = ['add' , 'list' , 'search' , 'lucky' , 'edit','error','404'];
        context = {'message': ''}
        mdb_key = ndb.Key('MoviesDb', 'list' or '*notitle*')
        if url in allows:
            if url == 'list':
                page = self.request.get('page');
                if page:
                    cursor = Cursor(urlsafe=page) 
                    moviesDb , next_cursor, more = MoviesDb.query_movies(mdb_key).fetch_page(self.ITEM_PER_PAGE,start_cursor=cursor);
                    context = {'message': '' , 'list_db' : moviesDb , 'next_cursor':next_cursor, 'more':more} 
                else:
                    moviesDb , next_cursor , more  = MoviesDb.query_movies(mdb_key).fetch_page(self.ITEM_PER_PAGE);
                    context = {'message': '' , 'list_db' : moviesDb,'next_cursor':next_cursor, 'more':more } 

            elif url == 'search': 
                text = self.request.get('q')
                if text:
                    searched = MoviesDb.search_name(text).fetch(30)
                    context = {'data': searched }
            elif url == 'lucky':
                searched = MoviesDb.lucky();
                context = {'data': searched }
            elif url == 'add':
                RecentList = self.getRecent()
                context = {'RecentList' : RecentList }
            elif url == 'edit':
                key = self.request.get('id');
                movie = ndb.Key(urlsafe=key).get()
                RecentList = self.getRecent()
                context = { 'RecentList' : RecentList , 'movie' : movie } 
           
        else:
            self.redirect('/view/error')

        self.render_response(url+'.html', **context)

    def post(self , **kwargs):
        item = kwargs.get('url') 
        allows = ['add','edit'];
        if item in allows:
            if item == 'add':
                mdb_key = ndb.Key('MoviesDb', 'list' or '*notitle*')
                Title = self.request.POST['Title'].strip();
                Year = self.request.POST['Year'].strip().replace(" ","-").lower();
                imdbID = self.request.POST['imdbID'].strip();
                Poster = self.request.POST['Poster'].strip();
                Type = 'movie';
                #TODO - Data validation should be here 
                try:
                    cndb = MoviesDb(parent=(mdb_key),name=Title,Year=Year,imdbID=imdbID , Poster=Poster , Type=Type )
                    cndb.put()
                    self.redirect('/view/list')
                except Exception as e:
                    print(e)
                    self.redirect('/view/error')
            elif item == 'edit':
                key = self.request.get('id');
                movie = ndb.Key(urlsafe=key).get()

                Title = self.request.POST['Title'].strip();
                Year = self.request.POST['Year'].strip().replace(" ","-").lower();
                imdbID = self.request.POST['imdbID'].strip();
                Poster = self.request.POST['Poster'].strip();

                movie.name = Title
                movie.Year = Year
                movie.imdbID = imdbID
                movie.Poster = Poster
                movie.put()

                context = {'message': 'Hello, world!' , 'movie' : movie }
                self.redirect('/view/list')
            else:  
                self.redirect('/view/404')
        else:
            self.redirect('/view/404')
    
    def getRecent(self):
        mdb_key = ndb.Key('MoviesDb', 'list' or '*notitle*')
        moviesDb = MoviesDb.query_movies(mdb_key).order(-MoviesDb.date).fetch(5);
        return moviesDb;


class HandlerWithError(BaseHandler):

    def get(self, **kwargs):
        #TODO -- can be  better debugging 
        context = {'message': 'Oops'}
        self.render_response('error.html', **context)



class ImportHandler(BaseHandler):
   
    def get(self):
        base_url = 'http://www.omdbapi.com:80/?type=movie&plot=short&s=true&apikey=ed29e7c7&tomatoes=False';
        number = 1;
        while(1):
            url = base_url+'&page='+str(number)
            print(url)
            response = urllib2.urlopen(url)
            data = eval(json.dumps(json.load(response))) 
            mdb_key = ndb.Key('MoviesDb', 'list' or '*notitle*')
            if 'Search' in data:
                for item in data['Search']:
                    cndb = MoviesDb(parent=(mdb_key),name=item['Title'],Year=item['Year'],imdbID=item['imdbID'] , Poster=item['Poster'] , Type=item['Type'] )
                    cndb.put()
                if number < int(data['totalResults'])/10:
                    number = number+1
                else:
                    break;
            else:
                break;
        context = {'message': ''}
        self.render_response('import.html', **context)