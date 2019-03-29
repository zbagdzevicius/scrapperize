import re
from translate import Translator as MicrosoftTranslator
from googletrans import Translator as GoogleTranslator
from bs4 import BeautifulSoup
from slugify import slugify
import urllib.request as urllib


class TextRefactorer:
    def __init__(self, source_language, destination_language, translator="microsoft"):
        self.translator_provider = translator
        if translator == "microsoft":
            self.translator = MicrosoftTranslator(
                to_lang=destination_language,
                from_lang=source_language,
                provider="microsoft",
                secret_access_key="8d9718e3499d479fb5cfee8e17e6f0d9",
            )
        if translator == "google":
            self.to_lang = destination_language
            self.from_lang = source_language
            self.translator = GoogleTranslator(
                service_urls=["translate.google.com", "translate.google.co.kr"]
            )

    def strip_anchors(self, data):
        p = re.compile(r"</?a.*?>")
        return p.sub("", data)

    def strip_braces(self, data):
        return (
            data.replace('"', "'").replace("  ", " ").replace("[", "").replace("]", "")
        )

    def refactor_p_tag(self, data):
        p = re.compile(r"<\s*?\D\s*[pP]\s?>")
        return p.sub("</p>", data)

    def refactor_em_tag(self, data):
        p = re.compile(r"<\s*?\D\s*[eE][mM]\s?>")
        return p.sub("</em>", data)

    def refactor_strong_tag(self, data):
        p = re.compile(r"<\s*?\D\s*[sS][tT][rR][oO][nN][gG]\s?>")
        return p.sub("</strong>", data)

    def refactor_span(self, data):
        p = re.compile(r"<\s?\W?\s?span\s?\W?\s?>")
        return p.sub("", data)

    def strip_tags(self, data):
        p = re.compile(
            r"""<\s*?/?\s*?(?!(?:p|P|strong|Strong)\b)[a-zA-Z](?:[^>"']|"[^"]*"|'[^']*')*\s*?>"""
        )
        return p.sub("", data)

    def remove_bad_content(self, data):
        data = self.refactor_p_tag(data)
        data = self.refactor_em_tag(data)
        data = self.refactor_strong_tag(data)
        data = self.refactor_span(data)
        data = self.strip_tags(data)
        data = self.strip_braces(data)
        return data

    def translate_string(self, data):
        try:
            data = self.remove_bad_content(data)
        except Exception as e:
            print("*******\n" * 5 + e + "empty data" + "*******\n" * 5)
        return self.translate(data)

    def translate(self, data):
        if self.translator_provider == "microsoft":
            return self.translator.translate(data)
        if self.translator_provider == "google":
            if isinstance(data, list):
                translations = self.translator.translate(
                    text=data, dest=self.to_lang, src=self.from_lang
                )
                translations_string = " ".join(
                    [translation.text for translation in translations]
                )
                return translations_string
            else:
                return self.translator.translate(
                    text=data, dest=self.to_lang, src=self.from_lang
                ).text

    def get_soup(self, url):
        return BeautifulSoup(
            urllib.urlopen(
                urllib.Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
                    },
                )
            ),
            "html.parser",
        )

    def string_to_slug(self, string):
        return slugify(string)
