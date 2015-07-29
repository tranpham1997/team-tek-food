import json
import sys
import urllib
import urllib2
import oauth2

api_host = 'api.yelp.com'
search_limit = 100
search_path = '/v2/search/'

consumer_key = 'AgdTIC8bGyXXBHeH9jr_FQ'
consumer_secret = 'RIYKujR2SsvPzD3b1MiNTwNuEfY'
TOKEN = 'MDvLguRKivyOwyEJvpyfAaungTo2X0_Q'
TOKEN_SECRET = 'DSj3F9-fp2THaUifP6-oeuWgLUA'
def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': consumer_key
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()

    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(term, location, sort):
#Query the Search API by a search term and location.
#Args:
    #term (str): The search term passed to the API.
    #location (str): The search location passed to the API.
#Returns:
    #dict: The JSON response from the request.
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': search_limit,
        'sort': sort
    }
    return request(api_host, search_path, url_params=url_params)
