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
        def search(term, location):
        #Query the Search API by a search term and location.
        #Args:
            #term (str): The search term passed to the API.
            #location (str): The search location passed to the API.
        #Returns:
            #dict: The JSON response from the request.
            term = restaurants
            url_params = {
                'term': term.replace(' ', '+'),
                'location': location.replace(' ', '+'),
                'limit': search_limit
            }
            return yelp.request(api_host, search_path, url_params=url_params)
        # Send a response.
        self.redirect('/search')
class SearchHandler(webapp2.RequestHandler):
    def get(self):
        pass
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/search', SearchHandler)
], debug=True)
