import requests
import json
import base64

username = "admin"
application_password = "0XKY QIJ3 mxsc nJER Cy9e TEn0"
url = "https://api.knocker.eu/wp-json/wp/v2"
encoded_colon = ":"
token_unencoded = username+":"+application_password
token = str(base64.standard_b64encode(token_unencoded.encode()).decode("utf-8"))
user_agent = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)'
headers = {"Authorization":f"Basic {token}",
 "User-Agent" : user_agent,
  'content-type': "application/json",
  "Access-Control-Allow-Headers":"Authorization, Content-Type",
  'Connection': 'keep-alive',
  'Host': 'api.knocker.eu',
  "Content-Encoding":"gzip"}

auth_data = {
    'grant_type': 'client_credentials'
}

with requests.Session() as s:
    s.headers.update(headers)
    print(s.headers)

    post = {"date": "2017-06-19T20:00:35",
            "title": "First REST API post",
            "slug": "rest-api-1",
            "status": "publish",
            "content": "this is the content post",
            "author": "1",
            "excerpt": "Exceptional post!",
            "format": "standard"
            }

    r = requests.post(url + "/posts", json=post, data=auth_data)
    print(r.content, r.status_code, r.reason, r.headers)
    # print("Your post is published on " + json.loads(r.content)["link"])