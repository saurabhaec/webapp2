from google.appengine.ext import ndb
import random

class MoviesDb(ndb.Model):
    """Models an individual Movies entry with content and date."""
    name = ndb.StringProperty()
    name_lower   = ndb.ComputedProperty(lambda self: self.name.lower())
    Year = ndb.StringProperty()
    imdbID = ndb.StringProperty()
    Poster = ndb.StringProperty()
    Type = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def query_movies(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.date)
    @classmethod
    def search_name(cls , text):
        limit = text[:-1] + chr(ord(text[-1]) + 1)
        return cls.query(cls.name >= text, cls.name < limit)
    @classmethod
    def lucky(cls):
 
        list_query = cls.query()
        list_query = list_query.filter(cls.Type == 'movie')
        list_keys = list_query.fetch(keys_only=True)
        list_keys = random.sample(list_keys, 12)
        lists = [list_key.get() for list_key in list_keys]
        return lists


        
     