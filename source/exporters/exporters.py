import six
from scrapy.exporters import XmlItemExporter
from scrapy.utils.python import is_listlike
from xml.sax.saxutils import XMLGenerator
from xml.sax.saxutils import escape
from xml.sax.saxutils import unescape
import hashlib

class MyXMLGenerator(XMLGenerator):
    def characters(self, content):
        if content:
            self._finish_pending_start_element()
            if not isinstance(content, str):
                content = str(content, self._encoding)
            self._write(unescape(content))

class MyXmlExportPipeline(XmlItemExporter):
    def __init__(self, file, **kwargs):
        self.item_element = kwargs.pop('item_element', 'product')
        self.root_element = kwargs.pop('root_element', 'products')
        self._configure(kwargs)
        if not self.encoding:
            self.encoding = 'UTF-8'
        self.xg = MyXMLGenerator(file, encoding=self.encoding)
        self.id_count = ''

    def export_item(self, item):
        id = item['title']
        self.id_count = int(hashlib.sha256(id.encode('utf-8')).hexdigest(), 16) % 10 ** 8
        self.id_count = self.id_count + 1
        self._beautify_indent(depth=1)
        self.xg.startElement(self.item_element, {'id': str(self.id_count)})
        self._beautify_newline()
        for name, value in self._get_serialized_fields(item, default_value=''):
            self._export_xml_field(name, value, depth=2)
        self._beautify_indent(depth=1)
        self.xg.endElement(self.item_element)
        self._beautify_newline(new_item=True)

    def _export_xml_field(self, name, serialized_value, depth):
        name = str(name).replace('&lt;','<')
        self._beautify_indent(depth=depth)
        self.xg.startElement(name, {})
        if hasattr(serialized_value, 'items'):
            self._beautify_newline()
            for subname, value in serialized_value.items():
                self._export_xml_field(subname, value, depth=depth+1)
            self._beautify_indent(depth=depth)
        elif is_listlike(serialized_value):
            self._beautify_newline()
            for value in serialized_value:
                self._export_xml_field('value', value, depth=depth+1)
            self._beautify_indent(depth=depth)
        elif isinstance(serialized_value, six.text_type):
            self._xg_characters(serialized_value)
        else:
            self._xg_characters(str(serialized_value))
        self.xg.endElement(name)
        self._beautify_newline()