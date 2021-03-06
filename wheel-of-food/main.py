#!/usr/bin/env python
import logging
import jinja2
import webapp2
import time
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


class User(ndb.Model):
    userEmail = ndb.StringProperty()
    food_preference = ndb.StringProperty(repeated = True)
    usePreferences = ndb.BooleanProperty()
    numResults = ndb.IntegerProperty()
# Initial page for website, offers login information
class MainHandler(webapp2.RequestHandler):
    def get(self):
        # mapsClient = client.Client(key = 'AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI')
        # self.response.write(geocoding.reverse_geocode(mapsClient, (40.714224,-73.961452)))
        error = self.request.get('error')
        user = users.get_current_user()
        profileInfo = True
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
        currentUser = None
        user = users.get_current_user()
        profileInfo = True
        if user:
            logout_url = users.create_logout_url('/')
            login_url = None
            username = user.email()
        else:  # user is not logged in
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
        r = random.randint(0, len(result["businesses"]) - 1)
        if 'distance' not in result["businesses"][0]:
            self.redirect('/?error=true')
        else:
            distance = int((result["businesses"][r]["distance"] * (.000621371192)) * 100)
            miles = (1.0 *distance)/100

        alert = result["businesses"][r]['image_url']
        name = result["businesses"][r]["name"]
        address= result["businesses"][r]["location"]["display_address"]
        typeRest =result["businesses"][r]["categories"][0][0]
        lat =results[0]['geometry']['location']['lat']
        lng= results[0]['geometry']['location']['lng']
        restImages =result["businesses"][r]['image_url']
        yelp_url = result['businesses'][r]['url']
        rest_lat = result['businesses'][r]['location']['coordinate']['latitude']
        rest_lng =  result['businesses'][r]['location']['coordinate']['longitude']
        food_preference =[]
        if user:
            if profileInfo == True:
                currentUser = User.query(User.userEmail == user.email()).get()
                # foodTypePreference1 = self.request.get('')
                # foodTypePreference2 = self.request.get('foodTypePreference2')
                # foodTypePreference3 = self.request.get('foodTypePreference3')
                # foodTypePreference4 = self.request.get('foodTypePreference4')
                # foodTypePreference5 = self.request.get('foodTypePreference5')
                # food_preference = [foodTypePreference1, foodTypePreference2, foodTypePreference3, foodTypePreference4, foodTypePreference5]
                food_preference = currentUser.food_preference
                for foodType in food_preference:
                    for i in range(0, len(result["businesses"])-1):
                        if result["businesses"][i]["categories"][0][0] == foodType:
                            name = result["businesses"][i]["name"]
                            address= result["businesses"][i]["location"]["display_address"]
                            typeRest =result["businesses"][i]["categories"][0][0]
                            restImages =result["businesses"][i]['image_url']
                            yelp_url = result['businesses'][i]['url']
                            rest_lat = result['businesses'][i]['location']['coordinate']['latitude']
                            rest_lng= result['businesses'][i]['location']['coordinate']['longitude']

        # First random restaurant shown in second screen
        variables = {
        'login_url': login_url,
        'logout_url': logout_url,
        'username': username,
        'location': location,
        'distance': miles,
        'name': name,
        'address': address,
        'type': typeRest,
        'lat': lat,
        'lng': lng,
        'restImages': restImages,
        'yelp_url': yelp_url,
        'rest_lat': rest_lat,
        'rest_lng': rest_lng,
        'alert': alert,
        'food_preference': food_preference
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
        urlRest = []
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
                rest_yelp_url = result['businesses'][j]['url']
                if miles <= disResults:
                    distanceRest.append(miles)
                    nameRest.append(name)
                    addressRest.append(address)
                    typeRest.append(typeR)
                    latRest.append(rest_lat)
                    lngRest.append(rest_lng)
                    urlRest.append(rest_yelp_url)
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
                rest_yelp_url = result['businesses'][j]['url']
                if miles <= disResults:
                    if typeResults == result["businesses"][j]["categories"][0][0]:
                        distanceRest.append(miles)
                        nameRest.append(name)
                        addressRest.append(address)
                        typeRest.append(typeR)
                        latRest.append(rest_lat)
                        lngRest.append(rest_lng)
                        urlRest.append(rest_yelp_url)
                        businIndex.append(j)
                        i = i + 1
                j = j + 1
                if j >= (len(result["businesses"])-1):
                    break;
            j = 0
            resFound = str(i) + " results found for " + typeResults + " food"
            if i == 1:
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
                    rest_yelp_url = result['businesses'][j]['url']
                    distanceRest.append(miles)
                    nameRest.append(name)
                    addressRest.append(address)
                    typeRest.append(typeR)
                    latRest.append(rest_lat)
                    lngRest.append(rest_lng)
                    urlRest.append(rest_yelp_url)
                    i = i + 1
                j = j + 1

                #Change Background according to type of food
        backgroundImg = ""
        backImg ={
            'American':"carls-jr-most-american-burger.jpg",
            'Arabian':"grilled-kangaroo.jpg",
            'Australian':"grilled-kangaroo.jpg",
            'Brazilian':"Traditional-Brazilian-Food.jpg",
            'Caribbean':"ropa-vieja.jpg",
            'Chinese':"295198-chinese-food.jpg",
            'Filipino':"photo-4.jpg",
            'French': "4e7fe1ec14f092326f000153-1317003759.jpeg",
            'German': "pastacabbage-germanfood-germanrecipes.jpg",
            'Greek':"Greek-Lentil-Salad-recipe-with-Feta-cheese-.jpg",
            'Indian':"ethnic.jpg",
            'Indonesian':"indo-salad.jpg",
            'Japanese':"5.jpg",
            'Latin American':"Paella.jpg",
            'Malaysian':"img_2800.jpg",
            'Mexican': "dsc_0491.jpg",
            'Middle Eastern':"sahara_falafel_plate.jpg",
            'Portuguese':"octopus.jpeg",
            'Thai':"Thai-food1.jpg",
            'Turkish':"photo-9.jpg",
            'Vegan': "vegan-dietyou.jpg",
            'Vegetarian':"muscle-building-food1.jpg",
            'Vietnamese': "img_5935.jpg"
        }
        backgroundImg = "../static/"+ backImg[typeResults]
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
            'urlRest': urlRest,
            'location': location,
            'letter': letter,
            'resFound': resFound,
            'backgroundImg': backgroundImg
            # 'backgroundImg': backgroundImg
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
        numResults = int(self.request.get('numResults'))
        newUser = User(userEmail=userEmail, food_preference=food_preference, numResults=numResults)
        newUser.put()
        time.sleep(.5)
        return self.redirect('/')

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('profile.html')
        user = users.get_current_user()
        userEmail = user.email()
        currentUser = User.query(User.userEmail == userEmail).get()
        foodTypePreference1 = currentUser.food_preference[0]
        foodTypePreference2 = currentUser.food_preference[1]
        foodTypePreference3 = currentUser.food_preference[2]
        foodTypePreference4 = currentUser.food_preference[3]
        foodTypePreference5 = currentUser.food_preference[4]
        numResults = currentUser.numResults
        profile_key_urlsafe = currentUser.key.urlsafe()
        template_variables = {'foodTypePreference1': foodTypePreference1,
                              'foodTypePreference2': foodTypePreference2,
                              'foodTypePreference3': foodTypePreference3,
                              'foodTypePreference4': foodTypePreference4,
                              'foodTypePreference5': foodTypePreference5,
                              'numResults': numResults,
                              'profile_key_urlsafe': profile_key_urlsafe}
        self.response.write(template.render(template_variables))

class EditHandler(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('editProf.html')
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
        currentUser = User.query(User.userEmail == userEmail).get()
        profile_key_urlsafe = currentUser.key.urlsafe()
        foodTypePreference1 = self.request.get('foodTypePreference1')
        foodTypePreference2 = self.request.get('foodTypePreference2')
        foodTypePreference3 = self.request.get('foodTypePreference3')
        foodTypePreference4 = self.request.get('foodTypePreference4')
        foodTypePreference5 = self.request.get('foodTypePreference5')
        food_preference = [foodTypePreference1, foodTypePreference2, foodTypePreference3, foodTypePreference4, foodTypePreference5]
        numResults = int(self.request.get('numResults'))
        currentUser.food_preference = food_preference
        currentUser.numResults = numResults
        currentUser.put()
        time.sleep(.5)
        return self.redirect('/profile?key=' + profile_key_urlsafe)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/search', SearchHandler),
    ('/location', LatLongHandler),
    ('/AboutApp', AboutAppHandler),
    ('/AboutUs', AboutUsHandler),
    ('/Sources', SourcesHandler),
    ('/newProfile', newProfileHandler),
    ('/profile', ProfileHandler),
    ('/editProfile', EditHandler)
], debug=True)
