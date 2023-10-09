from pathlib import Path
import json

import scrapy
import re
from bs4 import BeautifulSoup

def inline_links(html_string):
    # Parse the HTML
    soup = BeautifulSoup(html_string, 'html.parser')

    # Find all <a> elements and replace them with their combined representation
    for a_element in soup.find_all('a'):
        link_text = a_element.text
        link_href = a_element.get('href')
        if link_href and link_href.startswith('#'):
            continue
        if link_href and link_href.startswith('/'):
            link_href = 'https://uscis.gov' + link_href
        if link_text and link_href:
            combined_link = f'[{link_text}] ({link_href})'
            a_element.replace_with(combined_link)

    # Get the modified HTML as a string
    combined_string = soup.get_text(separator=' ').strip()

    return combined_string


def clean_string(input_string):
    # Compress multiple spaces into a single space
    #cleaned_string = re.sub(r'\s+', ' ', cleaned_string)
    cleaned_string = re.sub(r'\u00a0', ' ', input_string)
    cleaned_string = re.sub(r'\u2019', "'", cleaned_string)
    cleaned_string = re.sub(r'\u2013', "-", cleaned_string)
    cleaned_string = re.sub(r'\u201c', '"', cleaned_string)
    cleaned_string = re.sub(r'\u201d', '"', cleaned_string)

    # Replace special characters with a space
    cleaned_string = re.sub(r"[^\w\s\/\[\]\-,.():?=&%#'$]", ' ', cleaned_string)
    
    # Remove leading and trailing spaces
    cleaned_string = cleaned_string.strip()
    
    return cleaned_string


class USCISSpider(scrapy.Spider):
    name = "uscis"
    start_urls = [
        "https://www.uscis.gov/green-card"
    ]

    depth_limit = 5
    all_links = set()

    def notext(self, selector):
        text = selector.css('::text').get()
        return (not text) or (re.sub(r'\s+', '', text) == '')

    def parse_node(self, selectors, body, links):
        if not selectors:
            return

        for selector in selectors:
            #if 'class' in selector.attrib and selector.attrib['class'] == 'alert-message':
            #    text = ''.join(selector.xpath("*//text()").getall())
            #    alert_messages.append(clean_string(text))
            #    links = selector.css('a::attr(href)')
            #    alert_links += [item.extract() for item in links]
            #elif 'class' in selector.attrib and selector.attrib['class'] == 'content-accordion':
            #    headers = selector.css('.accordion__header')
            #    panels = selector.css('.accordion__panel')
            #    header_text = [item.xpath('text()').get() for item in headers]
            #    panel_text = [''.join(item.xpath('.//text()').getall()) for item in panels]
            #else:
            if self.notext(selector) and not selector.xpath('local-name()').get() == 'a':
                self.parse_node(selector.xpath('./*'), body, links)
            else:
                text = ''.join(selector.extract())
                text = inline_links(text)
                text = clean_string(text)
                body.append(text)
                link_nodes = selector.css('a::attr(href)')
                page_links = [item.extract() for item in link_nodes]
                links += [item for item in page_links if not item.startswith('#')]

        return

    def parse(self, response):
        page = response.url.split("/")[-1]
        filename = f"data/json/uscis-{page}.json"

        body = []
        links = []

        last_updated = response.xpath("//*[@id=\"block-uscis-design-content\"]/article/div[2]/div[2]/time/text()").get()
        breadcrumbs = response.xpath("//*[@id=\"block-uscis-design-breadcrumbs\"]/nav/ol/li/a/text()").getall()
        title = response.xpath("//*[@id=\"block-uscis-design-content\"]/article/div[1]/h1/span/text()").get()
        selectors = response.xpath("//*[@id=\"block-uscis-design-content\"]/article/div[1]/div/*")
        self.parse_node(selectors, body, links)

        Path(filename).write_text(json.dumps({
            'url' : response.url,
            'body' : body,
            'links' : list(set(links)),
            'title' : title,
            'last_updated' : last_updated,
            'breadcrumbs' : breadcrumbs
        }))

        depth = response.meta.get('depth')
        if depth < self.depth_limit and links:
            for link in links:
                if link not in self.all_links and link.startswith('/') and not link.endswith('.pdf'):
                    self.all_links.add(link)
                    yield response.follow(link, callback=self.parse)

        self.log(f"Saved file {filename}")
