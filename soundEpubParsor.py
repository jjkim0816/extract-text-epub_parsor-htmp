import sys
import ebooklib
from ebooklib import epub
from ebooklib import utils
from html.parser import HTMLParser

def select_caption_filter(tag, attrs):
    # print("start tag : ", tag, ", attrs : ", attrs)
    for k, v in attrs:
        if k == 'class':
            if v.find('caption') != -1 or v == 'gj3 bold':
                return True
    return False

class EpubHTMLParser(HTMLParser):

    # private variable
    __skip_html = False

    # public variable
    __extract_text__ = ""

    def handle_starttag(self, tag, attrs):
        self.__skip_html = select_caption_filter(tag, attrs)

    def handle_data(self, data):
        # print("data        : ", data, ", __skip_html : ", self.__skip_html)
        if self.__skip_html != True:
            create_data = data.strip()
            if len(create_data) != 0:
                create_data = create_data.replace('\r', '') # remove ^M
                create_data += "\n"
                self.__extract_text__ += create_data
        else:
            self.__skip_html = False

    def handle_endtag(self, tag):
        # print("end tag     : ", tag)
        pass

class EbookParsor:

    def __init__(self):
        self.title = ""
        self.creator = ""
        self.publisher = ""
        self.description = ""
        self.html_body = ""
        self.synthesis_texts = []

    def get_metadata_requires(self, book):
        self.title = book.get_metadata('DC', 'title')

    def get_metadata_options(self, book):
        self.creator = book.get_metadata('DC', 'creator')
        self.publisher = book.get_metadata('DC', 'publisher')
        self.description = book.get_metadata('DC', "description")

    def get_content_items(self, book):
        parser = EpubHTMLParser()
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # self.html_body += item.get_content().decode('utf-8')
                # print(self.html_body)

                # read per html tag
                self.html_body = item.get_body_content().decode('utf-8')
                parser.feed(self.html_body)
                if len(parser.__extract_text__) != 0:
                    self.synthesis_texts.append(parser.__extract_text__)
                parser.__extract_text__ = ""

        book.get_items().close()
        parser.close()
