#!/usr/bin/env python

import jinja2
import webapp2
from google.appengine.api import urlfetch
import json
import yelp
import random
from google.appengine.api import users
from google.appengine.ext import ndb
# from googlemaps import geocoding, client

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
# Information saved in user/email
class UserPreferences(ndb.Model):
    restType = ndb.StringProperty()
    numResults = ndb.IntegerProperty()
    distance = ndb.FloatProperty()
    date = ndb.DateProperty()

# Saving users in datastore
class User(ndb.Model):
    name = ndb.StringProperty()
    userId = ndb.StringProperty()

# Initial page for website, offers login information
class MainHandler(webapp2.RequestHandler):
    def get(self):
        # mapsClient = client.Client(key = 'AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI')
        # self.response.write(geocoding.reverse_geocode(mapsClient, (40.714224,-73.961452)))
        user = users.get_current_user()
        if user is None:
            login_url = users.create_login_url('/')
            logout_url = None
        else:
            logout_url = users.create_logout_url('/')
            login_url = None
        template_variables = {'login_url': login_url, 'logout_url': logout_url}
        template = env.get_template('home.html')
        self.response.write(template.render(template_variables))


class SearchHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            logout_url = users.create_logout_url('/')
            login_url = None
            username = user.email()
        else:
            login_url = None
            logout_url = None
            username = None
        location = self.request.get('location')
        gmaps_address = location.replace(' ', '+')
        geocode = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + str(gmaps_address) + '&key=AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI'
        json_content = urlfetch.fetch(geocode).content
        results = json.loads(json_content)['results']

        # Logic/process info - do a search with Yelp API
        result = yelp.search('restaurants', location, 0)
        numResults = self.request.get('number')
        if hasattr(result["businesses"][0], "distance"):
            distance = int((result["businesses"][0]["distance"] * (.000621371192)) * 100)
            miles = (1.0 *distance)/100
        else:
            miles = 'Unknown'

        # First random restaurant shown in second screen
        variables = {
        'login_url': login_url,
        'logout_url': logout_url,
        'username': username,
        'location': location,
        'distance': miles,
        'name': result["businesses"][0]["name"],
        'address': result["businesses"][0]["location"]["display_address"],
        'type': result["businesses"][0]["categories"][0][0],
        'lat': results[0]['geometry']['location']['lat'],
        'lng': results[0]['geometry']['location']['lng'],
        'rest_lat': result['businesses'][0]['location']['coordinate']['latitude'],
        'rest_lng': result['businesses'][0]['location']['coordinate']['longitude'],
        }
        template = env.get_template('results.html')
        # Print result in proper JSON - debugging purposes
        # self.response.headers['Content-Type'] = 'application/json'
        # obj = {'result': result}
        # self.response.out.write(json.dumps(result))
        # Send a response.
        self.response.write(template.render(variables))
    def post(self):
        letter = ['A','B','C','D','E','F','G','H','I','J']
        location = self.request.get('location')
        gmaps_address = location.replace(' ', '+')
        geocode = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + str(gmaps_address) + '&key=AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI'
        json_content = urlfetch.fetch(geocode).content
        results = json.loads(json_content)['results']
        result = yelp.search('restaurants', location, 0)
        distanceRest = []
        nameRest =[]
        addressRest = []
        typeRest =[]
        latRest = []
        lngRest = []
        numResults = int(self.request.get('number'))
        disResults = int(self.request.get('distance'))
        typeResults = self.request.get('restaurantType')
        i = 0
        j = 0
        alert = ""
        if typeResults == "No Preference":
            while i != numResults:
                if j >= (len(result["businesses"])-1):
                    break;
                distance = int((result["businesses"][j]["distance"] * (.000621371192))*100)
                miles= (1.0 *distance)/100
                name = result["businesses"][j]["name"]
                address = result["businesses"][j]["location"]["display_address"]
                typeR = result["businesses"][j]["categories"][0][0]
                rest_lat = result['businesses'][j]['location']['coordinate']['latitude']
                rest_lng = result['businesses'][j]['location']['coordinate']['longitude']
                if miles <= disResults:
                    distanceRest.append(miles)
                    nameRest.append(name)
                    addressRest.append(address)
                    typeRest.append(typeR)
                    latRest.append(rest_lat)
                    lngRest.append(rest_lng)
                    i = i + 1
                j = j + 1
        else:
            alert = "Hi"
            typeResults = typeResults.lower()
            while i != numResults:
                if j >= (len(result["businesses"])-1):
                    break;
                distance = int((result["businesses"][j]["distance"] * (.000621371192))*100)
                miles= (1.0 *distance)/100
                name = result["businesses"][j]["name"]
                address = result["businesses"][j]["location"]["display_address"]
                typeR = result["businesses"][j]["categories"][0][0]
                rest_lat = result['businesses'][j]['location']['coordinate']['latitude']
                rest_lng = result['businesses'][j]['location']['coordinate']['longitude']
                if miles <= disResults:
                    if typeResults is result["businesses"][j]["categories"][0][0].lower():
                        distanceRest.append(miles)
                        nameRest.append(name)
                        addressRest.append(address)
                        typeRest.append(typeR)
                        latRest.append(rest_lat)
                        lngRest.append(rest_lng)
                        i = i + 1
                j = j + 1
            name = result["businesses"][i]["name"]
            address = result["businesses"][i]["location"]["display_address"]
            typeR = result["businesses"][i]["categories"][0][0]
            rest_lat = result['businesses'][j]['location']['coordinate']['latitude']
            rest_lng = result['businesses'][j]['location']['coordinate']['longitude']
            distanceRest.append(miles)
            nameRest.append(name)
            addressRest.append(address)
            typeRest.append(typeR)
            latRest.append(rest_lat)
            lngRest.append(rest_lng)
        variables = {
            'lat': results[0]['geometry']['location']['lat'],
            'lng': results[0]['geometry']['location']['lng'],
            'latRest': latRest,
            'lngRest': lngRest,
            'distanceRest': distanceRest,
            'nameRest': nameRest,
            'addressRest': addressRest,
            'typeRest': typeRest,
            'latRest': latRest,
            'lngRest': lngRest,
            'location': location,
            'letter': letter,
            'alert': alert
            }
        template = env.get_template('resultsfilter.html')
        self.response.write(template.render(variables))

class LatLongHandler(webapp2.RequestHandler):
    def get(self):
        # template = env.get_template('home.html')
        lat = self.request.get('lat')
        lon = self.request.get('lon')
        string = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='+ str(lat) + ',' + str(lon) + '&key=AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI'
        json_content = urlfetch.fetch(string).content
        results = json.loads(json_content)['results']
        address = results[0]['formatted_address'].replace(' ', '+')
        # variables = {'address': address}
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

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('profile.html')
        user = users.get_current_user()
        if user is None:
            login_url = users.create_login_url('/')
            logout_url = None
            username = None
        else:
            logout_url = users.create_logout_url('/')
            login_url = None
            username = user.email()
        template_variables = {'login_url': login_url, 'logout_url': logout_url, 'username': username}
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/search', SearchHandler),
    ('/location', LatLongHandler),
    ('/AboutApp', AboutAppHandler),
    ('/AboutUs', AboutUsHandler),
    ('/Sources', SourcesHandler),
    ('/profile', ProfileHandler),
], debug=True)
