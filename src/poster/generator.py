import json
from random import choice

with open('2018-08-18_okidario_posts.json', encoding="utf8") as f:
    data = json.load(f)

domain= 'https://knocker.eu/#/'
random_slug = choice(data)['post_slug']
post_link = domain + random_slug
print(post_link)