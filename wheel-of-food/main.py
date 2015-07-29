#!/usr/bin/env python

import jinja2
import webapp2
from google.appengine.api import urlfetch
import json
import yelp
import random
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
        location = self.request.get('location')
        result = yelp.search('restaurants', location, 0)
        numResults = self.request.get('number')
        distance = int((result["businesses"][0]["distance"] * (.000621371192)) * 100)
        miles = (1.0 *distance)/100
        variables = {
        'location': location,
        'distance': miles,
        'name': result["businesses"][0]["name"],
        'address': result["businesses"][0]["location"]["display_address"],
        'type': result["businesses"][0]["categories"][0][0]
        }
        template = env.get_template('results.html')
        # Print result in proper JSON - testing purposes
        # self.response.headers['Content-Type'] = 'application/json'
        # obj = {'result': result}
        # self.response.out.write(json.dumps(result))
        # Process response
        self.response.write(template.render(variables))
    def post(self):
        location = self.request.get('location')
        result = yelp.search('restaurants', location, 0)
        distanceRest = []
        nameRest =[]
        addressRest = []
        typeRest =[]
        numResults = int(self.request.get('number'))
        for i in range(0,numResults):
            distance = int((result["businesses"][i]["distance"] * (.000621371192))*100)
            miles= (1.0 *distance)/100
            name = result["businesses"][i]["name"]
            address = result["businesses"][i]["location"]["display_address"]
            typeR = result["businesses"][i]["categories"][0][0]
            distanceRest.append(miles)
            nameRest.append(name)
            addressRest.append(address)
            typeRest.append(typeR)
        variables ={
            'distanceRest': distanceRest,
            'nameRest': nameRest,
            'addressRest': addressRest,
            'typeRest':typeRest
        }
        template = env.get_template('resultsfilter.html')
        self.response.write(template.render(variables))

class LatLongHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('home.html')
        lat = self.request.get('lat')
        lon = self.request.get('lon')
        string = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='+ str(lat) + ',' + str(lon) + '&key=AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI'
        json_content = urlfetch.fetch(string).content
        results = json.loads(json_content)['results']
        address = results[0]['formatted_address']
        variables = {
        'address' : address}
        self.redirect('../search?location=' + address)

class AboutAppHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('aboutApp.html')
        self.response.write(template.render())

class AboutUsHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('aboutDevelopers.html')
        self.response.write(template.render())

class SourcesHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('sources.html')
        self.response.write(template.render())

class FilterHandler(webapp2.RequestHandler):
    def get(self):
        numResults = self.request.get('number')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/search', SearchHandler),
    ('/location', LatLongHandler),
    ('/AboutApp', AboutAppHandler),
    ('/AboutUs', AboutUsHandler),
    ('/Sources', SourcesHandler)
], debug=True)
