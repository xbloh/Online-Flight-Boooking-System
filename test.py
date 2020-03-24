# API to get airport names

import requests
import json

url = "https://tripadvisor1.p.rapidapi.com/airports/search"

country_name = "singapore"

querystring = {"locale":"en_US","query":country_name}

headers = {
    'x-rapidapi-host': "tripadvisor1.p.rapidapi.com",
    'x-rapidapi-key': "784f87795dmsh204fa07eae65ddep17e039jsnabff7d2d4581"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

for result in json.loads(response.text):
    print(result['display_sub_title'])
