import scrapy
from AcmSpider.items import CodeforcesItem
from AcmSpider.config.codeforces_config import START_URLS


class CodeforcesSpider(scrapy.Spider):
    name = 'codeforces'
    allowed_domains = ['codeforces.com']
    start_urls = START_URLS

    def parse(self, response):
        items = []

        # //*[@id="pageContent"]/div[2]/div[5]/div[2]/div/h1/a
        # //*[@id="pageContent"]/div[2]/div[5]/div[2]/ul/li[1]/span[1]
        # //*[@id="pageContent"]/div[4]/div/div[7]/div[1]/div[1]/div[1]
        for each in response.xpath('*[@id="pageContent"]'):
            item = CodeforcesItem()
            id = each.xpath('/div[2]/div[5]/div[2]/div/h1/a/text()').extract()
            rating = int(each.xpath('/div[2]/div[5]/div[2]/ul/li[1]/span[1]/text()').extract())
            solve_problem_number = int(each.xpath('/div[4]/div/div[7]/div[1]/div[1]/div[1]/text()').extract())

            item['id'] = id[0]
            item['reating'] = rating[0]
            item['solve_problem_number'] = solve_problem_number[0]

            items.append(item)

        return items
