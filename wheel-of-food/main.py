#!/usr/bin/env python
import logging
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
        error = self.request.get('error')
        user = users.get_current_user()
        #profileInfo = True
        if user is None:
            login_url = users.create_login_url('/')
            logout_url = None
            profileInfo = False
            profile_key_urlsafe = None
        else:
            logout_url = users.create_logout_url('/')
            login_url = None
            userEmail = user.email()
            userID = user.user_id()
            currentUser = User.query(User.userEmail == userEmail).fetch()
            if currentUser == []:
                profileInfo = False
                profile_key_urlsafe = None
            else:
                profileInfo = True
                logging.error(currentUser)
                profile_key_urlsafe = currentUser[0].key.urlsafe()
        template_variables = {'login_url': login_url, 'logout_url': logout_url, 'profileInfo': profileInfo, 'profile_key_urlsafe': profile_key_urlsafe, 'error': error}
        template = env.get_template('home.html')
        self.response.write(template.render(template_variables))

class SearchHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            logout_url = users.create_logout_url('/')
            login_url = None
            username = user.nickname()
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
        miles = ''
        result = yelp.search('restaurants', location, 0)
        numResults = self.request.get('number')
        if 'distance' not in result["businesses"][0]:
            self.redirect('/?error=true')
        else:
            distance = int((result["businesses"][0]["distance"] * (.000621371192)) * 100)
            miles = (1.0 *distance)/100

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
        #'restImages': results["businesses"][0]['image_url'][0],
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
        businIndex = []
        numResults = int(self.request.get('number'))
        disResults = int(self.request.get('distance'))
        typeResults = self.request.get('restaurantType')
        i = 0
        j = 0
        resFound = ""
        if typeResults == "No Preference":
            while i != numResults:
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
                    businIndex.append(j)
                    i = i + 1
                j = j + 1
                if j >= (len(result["businesses"])-1):
                    break;
        else:
            # alert = "Hi"
            typeResults = typeResults
            while i != numResults:
                distance = int((result["businesses"][j]["distance"] * (.000621371192))*100)
                miles= (1.0 *distance)/100
                name = result["businesses"][j]["name"]
                address = result["businesses"][j]["location"]["display_address"]
                typeR = result["businesses"][j]["categories"][0][0]
                rest_lat = result['businesses'][j]['location']['coordinate']['latitude']
                rest_lng = result['businesses'][j]['location']['coordinate']['longitude']
                if miles <= disResults:
                    if typeResults == result["businesses"][j]["categories"][0][0]:
                        distanceRest.append(miles)
                        nameRest.append(name)
                        addressRest.append(address)
                        typeRest.append(typeR)
                        latRest.append(rest_lat)
                        lngRest.append(rest_lng)
                        businIndex.append(j)
                        i = i + 1
                j = j + 1
                if j >= (len(result["businesses"])-1):
                    break;
            j = 0
            resFound = str(i) + " results found for " + typeResults + " food"
            if i ==1:
                resFound = str(i) + " result found for " + typeResults + " food"
            while i != numResults:
                distance = int((result["businesses"][j]["distance"] * (.000621371192))*100)
                miles= (1.0 *distance)/100
                if miles <= disResults:
                    for check in businIndex:
                        alert = "uphomes"
                        if check == j:
                            j = j + 1
                    name = result["businesses"][j]["name"]
                    address = result["businesses"][j]["location"]["display_address"]
                    typeR = result["businesses"][j]["categories"][0][0]
                    rest_lat = result['businesses'][j]['location']['coordinate']['latitude']
                    rest_lng = result['businesses'][j]['location']['coordinate']['longitude']
                    distanceRest.append(miles)
                    nameRest.append(name)
                    addressRest.append(address)
                    typeRest.append(typeR)
                    latRest.append(rest_lat)
                    lngRest.append(rest_lng)
                    i = i + 1
                j = j + 1

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
            'resFound': resFound
            }
        template = env.get_template('resultsfilter.html')
        self.response.write(template.render(variables))
        # letter = ['A','B','C','D','E','F','G','H','I','J']
        # location = self.request.get('location')
        # gmaps_address = location.replace(' ', '+')
        # geocode = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + str(gmaps_address) + '&key=AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI'
        # json_content = urlfetch.fetch(geocode).content
        # results = json.loads(json_content)['results']
        # result = yelp.search('restaurants', location, 0)
        # disResults = self.request.get('distance')
        # businIndex = []
        # distanceRest = []
        # nameRest =[]
        # addressRest = []
        # typeRest =[]
        # latRest = []
        # lngRest = []
        # numResults = int(self.request.get('number'))
        # # if "distance" in result["businesses"][0]:
        # #     disResults = int(self.request.get('distance'))
        # typeResults = self.request.get('restaurantType')
        # i = 0
        # j = 0
        # searchResults = ""
        # #alert = ""
        # if typeResults == "No Preference":
        #     alert = "yo"
        #     while i != numResults:
        #         # if j >= (len(result["businesses"])-1):
        #         #     break;
        #         # Checks if miles exists
        #         miles = 0
        #         if "distance" in result["businesses"][0]:
        #             distance = int((result["businesses"][j]["distance"] * (.000621371192))*100)
        #             miles= (1.0 *distance)/100
        #         else:
        #             miles = "Unknown"
        #         name = result["businesses"][j]["name"]
        #         address = result["businesses"][j]["location"]["display_address"]
        #         typeR = result["businesses"][j]["categories"][0][0]
        #         rest_lat = result['businesses'][j]['location']['coordinate']['latitude']
        #         rest_lng = result['businesses'][j]['location']['coordinate']['longitude']
        #         if "distance" in result["businesses"][0]:
        #             if miles <= disResults:
        #                 distanceRest.append(miles)
        #                 nameRest.append(name)
        #                 addressRest.append(address)
        #                 typeRest.append(typeR)
        #                 latRest.append(rest_lat)
        #                 lngRest.append(rest_lng)
        #                 businIndex.append(j)
        #                 i = i + 1
        #         else:
        #             distanceRest.append(miles)
        #             nameRest.append(name)
        #             addressRest.append(address)
        #             typeRest.append(typeR)
        #             latRest.append(rest_lat)
        #             lngRest.append(rest_lng)
        #             businIndex.append(j)
        #             i = i + 1
        #         j = j + 1
        # else:
        #     alert = "Hi"
        #     typeResults = typeResults
        #     while i != numResults:
        #         # checks if distance exists
        #         #result["businesses"][j]["distance"]:
        #         # distance = int((result["businesses"][j]["distance"] * (.000621371192))*100)
        #         # miles= (1.0 *distance)/100
        #         #miles = "Unknown"
        #         # if j >= (len(result["businesses"])-1):
        #         #     break;
        #         miles = 0
        #         if "distance" in result["businesses"][j]:
        #             alert = "sup"
        #             distance = int((result["businesses"][j]["distance"] * (.000621371192))*100)
        #             miles= (1.0 *distance)/100
        #         else:
        #             miles = "Unknown"
        #         name = result["businesses"][j]["name"]
        #         address = result["businesses"][j]["location"]["display_address"]
        #         typeR = result["businesses"][j]["categories"][0][0]
        #         rest_lat = result['businesses'][j]['location']['coordinate']['latitude']
        #         rest_lng = result['businesses'][j]['location']['coordinate']['longitude']
        #         # if miles <= disResults or miles is "Unknown":
        #         alert = result["businesses"][j]["categories"][0][1]
        #         if typeResults == result["businesses"][j]["categories"][0][0]:
        #         #         distanceRest.append(miles)
        #             alert = "I guess"
        #             if "distance" in result["businesses"][j]:
        #                 if miles <= disResults:
        #                     if typeResults is result["businesses"][j]["categories"][0][0]:
        #                         distanceRest.append(miles)
        #                         nameRest.append(name)
        #                         addressRest.append(address)
        #                         typeRest.append(typeR)
        #                         latRest.append(rest_lat)
        #                         lngRest.append(rest_lng)
        #                         businIndex.append(j)
        #                         i = i + 1
        #             else:
        #                 distanceRest(miles)
        #                 nameRest.append(name)
        #                 addressRest.append(address)
        #                 typeRest.append(typeR)
        #                 latRest.append(rest_lat)
        #                 lngRest.append(rest_lng)
        #                 businIndex.append(j)
        #                 i = i + 1
        #         j = j + 1
        #         if j >= (len(result["businesses"])-1):
        #             break;
        # j = 0
        # if i != numResults:
        #     searchResults = str(i) + " results found for " + typeResults
        #     while i  != numResults:
        #         # checks if distance exists
        #         #if result["businesses"][j]["distance"] is False:
        #         miles = 0
        #         for check in businIndex:
        #             if check == j:
        #                 j = j + 1
        #         if "distance" in result["businesses"][j]:
        #             distance = int((result["businesses"][j]["distance"] * (.000621371192))*100)
        #             miles= (1.0 *distance)/100
        #         else:
        #             miles = "Unknown"
        #         #else:
        #         #    miles = "Unknown"
        #         name = result["businesses"][j]["name"]
        #         address = result["businesses"][j]["location"]["display_address"]
        #         typeR = result["businesses"][j]["categories"][0][0]
        #         rest_lat = result['businesses'][j]['location']['coordinate']['latitude']
        #         rest_lng = result['businesses'][j]['location']['coordinate']['longitude']
        #         distanceRest.append(miles)
        #         nameRest.append(name)
        #         addressRest.append(address)
        #         typeRest.append(typeR)
        #         latRest.append(rest_lat)
        #         lngRest.append(rest_lng)
        #         i = i + 1
        # variables = {
        #     'lat': results[0]['geometry']['location']['lat'],
        #     'lng': results[0]['geometry']['location']['lng'],
        #     'latRest': latRest,
        #     'lngRest': lngRest,
        #     'distanceRest': distanceRest,
        #     'nameRest': nameRest,
        #     'addressRest': addressRest,
        #     'typeRest': typeRest,
        #     'latRest': latRest,
        #     'lngRest': lngRest,
        #     'location': location,
        #     'letter': letter,
        #     'alert': alert,
        #     'searchResults':searchResults
        #     }
        # template = env.get_template('resultsfilter.html')
        # self.response.write(template.render(variables))

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

class User(ndb.Model):
    userEmail = ndb.StringProperty()
    food_preference = ndb.StringProperty(repeated = True)
    usePreferences = ndb.BooleanProperty()
    numResults = ndb.IntegerProperty()

class newProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('newProfile.html')
        user = users.get_current_user()
        if user:
            logout_url = users.create_logout_url('/')
            login_url = None
            username = user.nickname()
        else:
            login_url = None
            logout_url = None
            username = None
        template_variables = {'login_url': login_url, 'logout_url': logout_url, 'username': username}
        self.response.write(template.render(template_variables))
    def post(self):
        user = users.get_current_user()
        userEmail = user.email()
        username = self.request.get('username')
        foodTypePreference1 = self.request.get('foodTypePreference1')
        foodTypePreference2 = self.request.get('foodTypePreference2')
        foodTypePreference3 = self.request.get('foodTypePreference3')
        foodTypePreference4 = self.request.get('foodTypePreference4')
        foodTypePreference5 = self.request.get('foodTypePreference5')
        food_preference = [foodTypePreference1, foodTypePreference2, foodTypePreference3, foodTypePreference4, foodTypePreference5]
        usePreferences = bool(self.request.get('usePreferences'))
        numResults = int(self.request.get('numResults'))
        newUser = User(userEmail=userEmail, food_preference=food_preference, usePreferences=usePreferences, numResults=numResults)
        newUser.put()
        return self.redirect('/')

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('profile.html')
        user = users.get_current_user()
        userEmail = user.email()
        currentUser = User.query(User.userEmail == userEmail).fetch()
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/search', SearchHandler),
    ('/location', LatLongHandler),
    ('/AboutApp', AboutAppHandler),
    ('/AboutUs', AboutUsHandler),
    ('/Sources', SourcesHandler),
    ('/newProfile', newProfileHandler),
    ('/profile', ProfileHandler)
], debug=True)
