from wordpress_xmlrpc import WordPressPost, WordPressMedia, WordPressTerm
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts, media
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.compat import xmlrpc_client
import json
import urllib.request as urllib
import mimetypes
from xmlrpc.client import Transport

class CustomTransport(Transport):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"


username = 'WORDPRESS_USERNAME'
password = 'WORDPRESS_PASSWORD'
wp = Client('http://rehorned.com/xmlrpc.php', username=username,
            password=password)
post = WordPressPost()


def post_to_wp(title, slug, category_list, content, excerpt, thumbnail):
    post.title = title
    post.slug = slug
    post.terms_names = {
        'category': category_list
    }
    post.content = content
    post.excerpt = excerpt
    post.post_status = 'publish'
    post.thumbnail = thumbnail
    wp.call(NewPost(post))


with open('2018-08-18_okidario_posts.json', encoding="utf8") as f:
    data = json.load(f)

for _post in data:
    try:
        picture = urllib.urlopen(_post['image_src'])
        imageName = picture.url.split('/')[-1]
        imageType = mimetypes.guess_type(str(picture.url))[0]

        data = {
            'name': imageName,
            'type': imageType,
        }

        data['bits'] = xmlrpc_client.Binary(picture.read())
        response = wp.call(media.UploadFile(data))
        attachment_id = response['id']

        post_to_wp(title=_post['title'],
                slug=_post['post_slug'],
                category_list=[_post['category']],
                content=_post['post_content'],
                excerpt=_post['post_excerpt'],
                thumbnail=attachment_id)
    except:
        pass

