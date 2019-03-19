import re
from translate import Translator
from bs4 import BeautifulSoup
from slugify import slugify
import urllib.request as urllib

class TextRefactorer():
    def __init__(self, source_language, destination_language):
        self.translator = Translator(to_lang=destination_language, from_lang=source_language, provider='microsoft', secret_access_key='cf0e74ec363149678a101dc4dad90b5a')

    def strip_anchors(self, data):
        p = re.compile(r'</?a.*?>')
        return p.sub('', data)

    def strip_braces(self, data):
        return data.replace('"', "'").replace('  ', ' ').replace('[', '').replace(']', '')

    def refactor_p_tag(self, data):
        p = re.compile(r'<\s*?\D\s*[pP]\s?>')
        return p.sub('</p>', data)

    def refactor_em_tag(self, data):
        p = re.compile(r'<\s*?\D\s*[eE][mM]\s?>')
        return p.sub('</em>', data)

    def refactor_strong_tag(self, data):
        p = re.compile(r'<\s*?\D\s*[sS][tT][rR][oO][nN][gG]\s?>')
        return p.sub('</strong>', data)

    def refactor_span(self, data):
        p = re.compile(r'<\s?\W?\s?span\s?\W?\s?>')
        return p.sub('', data)

    def strip_tags(self, data):
        p = re.compile(
            r"""<\s*?/?\s*?(?!(?:p|P|strong|Strong)\b)[a-zA-Z](?:[^>"']|"[^"]*"|'[^']*')*\s*?>""")
        return p.sub('', data)

    def remove_bad_content(self, data):
        data = self.refactor_p_tag(data)
        data = self.refactor_em_tag(data)
        data = self.refactor_strong_tag(data)
        data = self.refactor_span(data)
        data = self.strip_tags(data)
        data = self.strip_braces(data)
        return data

    def translate_string(self, data):
        data = self.remove_bad_content(data)
        return self.translator.translate(data)

    def get_soup(self, url):
        return BeautifulSoup(urllib.urlopen(urllib.Request(url, headers={'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
                                                                         })), 'html.parser')
    
    def string_to_slug(self, string):
        return slugify(string)