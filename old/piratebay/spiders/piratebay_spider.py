from scrapy.spiders import Spider
from scrapy import Selector

import urllib
import urlparse

from piratebay.items import UniversalItem

class LimetorrentSpider(Spider):
    name = "limetorrent"
    allowed_domains = ["limetorrents.cc"]
    with open('links/limetorrents.txt', 'r') as file:
        start_urls = [i.strip() for i in file.readlines()]

    def parse(self, response):
        yield {
                'link': response.css('table.table2 td.tdleft div.tt-name a::attr(href)').extract()
                #'author': quote.css('small.author::text').extract_first(),
                #'tags': quote.css('div.tags a.tag::text').extract(),
        }

def url_fix(s, charset='utf-8'):
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))
