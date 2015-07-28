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
        # self.response.write(geocoding.reverse_geocode(mapsClient, (40.714224,-73.961452)))
        template = env.get_template('home.html')
        self.response.write(template.render())

class SearchHandler(webapp2.RequestHandler):
    def get(self):
        pass

class SearchHandler(webapp2.RequestHandler):
    def get(self):
        location = self.request.get('location')
        # Logic/process info - do a search with Yelp API
        result = yelp.search('restaurants', location, 1)
        # Print result in proper JSON - testing purposes
        self.response.headers['Content-Type'] = 'application/json'
        obj = {'result': result}
        self.response.out.write(json.dumps(result))
        # Process response
        # self.response.out.write(result["businesses"][0]["name"])


class LocationHandler(webapp2.RequestHandler):
    def get(self):
        # json_content = urlfetch.fetch('https://maps.googleapis.com/maps/api/geocode/json?latlng=40.714224,-73.961452&key=AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI').content
        # results = json.loads(json_content)['results']
        # address = results[0]['formatted address']
        # variables = {
        # 'address' : address
        # }
        template = env.get_template('glhome.html')
        self.response.write(template.render())

class LatLongHandler(webapp2.RequestHandler):
    def get(self):
        lat = self.request.get('lat')
        lon = self.request.get('lon')
        self.response.write(lat + ", " + lon)
        string = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='+ lat + ',' + long + '&key=AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI'
        json_content = urlfetch.fetch(string).content
        results = json.loads(json_content)['results']
        address = results[0]['formatted address']
        variables = {
        'address' : address
         }
        template = env.get_template('home.html')
        self.response.write(template.render(variables))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/search', SearchHandler),
    ('/geo', LocationHandler),
    ('/location', LatLongHandler)
], debug=True)
