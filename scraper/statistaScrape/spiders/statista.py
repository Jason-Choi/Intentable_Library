import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import re

from scrapy.utils.project import get_project_settings
from statistaScrape.items import StatistaItem


class StatistaSpider(scrapy.Spider):
    name = "statista"
    
    allowed_domains = ['statista.com']
    
    def start_requests(self):
        start = get_project_settings().get("DOWNLOAD_START_PAGE")
        end = get_project_settings().get("DOWNLOAD_END_PAGE")
        for i in range(end, start, -1):
            yield scrapy.Request('https://www.statista.com/statistics/popular/p/' + str(i) + "/", callback=self.parse_list)

    def parse_list(self, response):
        le = LinkExtractor(allow=r'statistics/.')
        for link in le.extract_links(response):

            if "popular" not in link.url and "recent" not in link.url:
                
                yield scrapy.Request(link.url, callback=self.parse_data)

    def parse_data(self, response):
        item = StatistaItem()
        item['title'] = response.xpath(
            '//h2[@class="sectionHeadline sectionHeadline--statistic"]/span/text()').get().replace("\n", "").strip()
        item['market'] = response.xpath(
            '//div[@aria-label="breadcrumbs"]/ul/li[1]/a/span/text()').get()
        item['topic'] = response.xpath(
            '//div[@aria-label="breadcrumbs"]/ul/li[2]/a/span/text()').get()
        item['spec'] = response.xpath(
            '//div[@data-chart-vars-name="options"]/@data-chart-vars').get()
        item['caption'] = self.getCaption(response)
        item["id"] = response.url.split("/")[4]
        if item['spec']:
            print(item['title'], item['id'])
        yield item

    def getCaption(self, response):
        captions = response.xpath('//div[@id="readingAidText"]').getall()
        return "".join([re.sub('(<([^>]+)>)', '', caption) for caption in captions]).strip()
        