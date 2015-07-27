#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api import urlfetch
import json
# from googlemaps import geocoding, client
class MainHandler(webapp2.RequestHandler):
    def get(self):
        # mapsClient = client.Client(key = 'AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI')
        self.response.write('Hello world!')
        json_content = urlfetch.fetch('https://maps.googleapis.com/maps/api/geocode/json?latlng=40.714224,-73.961452&key=AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI').content
        results = json.loads(json_content)['results']

        # self.response.write(geocoding.reverse_geocode(mapsClient, (40.714224,-73.961452)))
        self.response.write(results[0]['formatted_address']
        )

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
