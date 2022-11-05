import scrapy


class VjudgecontestSpider(scrapy.Spider):
    name = 'vjudgecontest'
    allowed_domains = ['vjudge.csgrandeur.cn']
    # start_urls = ['https://vjudge.csgrandeur.cn']

    def start_requests(self):
        url = 'https://vjudge.csgrandeur.cn/user/login'

        yield scrapy.FormRequest(
            url=url,
            method='POST',
            formdata={
                'username': 'XiaoyuHan',
                'password': 'ybzwanqad'
            },
            callback=self.parse)

    def parse(self, response):
        with open('vjudge.txt', 'w+') as file:
            file.write(str(response.headers.get('Set-Cookie')))
        print('Login Successful')



