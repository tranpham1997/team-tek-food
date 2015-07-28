#!/usr/bin/env python

import jinja2
import webapp2
from google.appengine.api import urlfetch
import json
import yelp
# from googlemaps import geocoding, client

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        # mapsClient = client.Client(key = 'AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI')
        json_content = urlfetch.fetch('https://maps.googleapis.com/maps/api/geocode/json?latlng=40.714224,-73.961452&key=AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI').content
        results = json.loads(json_content)['results']

        # self.response.write(geocoding.reverse_geocode(mapsClient, (40.714224,-73.961452)))
        self.response.write(results[0]['formatted_address'])
        template = env.get_template('home.html')
        self.response.write(template.render())
    def post(self):
        # Get information from request
        location = self.request.get('Location')
        return location
        # Logic/process info - do a search with Yelp API
        result = yelp.search('restaurants', location)
        # Send a response.
        self.redirect('/search')
class SearchHandler(webapp2.RequestHandler):
    def get(self):
<<<<<<< HEAD
        pass

class LocationHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('glhome.html')
        self.response.write(template.render())

    def post(self):
        pass

=======
        self.response.write(result)
>>>>>>> 27aea70423d34c542a8eb2b8cbc6931898f9a013
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/search', SearchHandler),
    ('/geo', LocationHandler)
], debug=True)
