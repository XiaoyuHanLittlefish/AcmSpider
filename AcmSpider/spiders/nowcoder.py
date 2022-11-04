import scrapy
from AcmSpider.items import NowcoderItem
from AcmSpider.config.nowcoder_config import START_URLS


class NowcoderSpider(scrapy.Spider):
    name = 'nowcoder'
    allowed_domains = ['ac.nowcoder.com']
    start_urls = START_URLS

    def parse(self, response):
        items = []
        
        # /html/body/div/div[2]/div[1]/div[1]/div/div[2]/div[1]/a[1]
        # /html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/div[2]/div[1]/div/a
        # /html/body/div[1]/div[2]/div[2]/section/div[1]/div[2]/div
        for each in response.xpath('/html/body/div[1]/div[2]'):
            item = NowcoderItem()
            name = each.xpath('div[1]/div[1]/div/div[2]/div[1]/a[1]/text()').extract()
            rating = each.xpath('div[1]/div[1]/div/div[2]/div[2]/div[1]/div/a/text()').extract()
            solve_problem_number = each.xpath('div[2]/section/div[1]/div[2]/div/text()').extract()

            item['name'] = name[0]
            item['rating'] = rating[0]
            item['solve_problem_number'] = solve_problem_number[0]

            items.append(item)

        return items
