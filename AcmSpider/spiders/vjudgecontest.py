import scrapy

from AcmSpider.config.vjudge_config import LOGIN_URL, LOGIN_FORM_DATA, COOKIE_PATH, GROUP_LIST, VJUDGE_URL


class VjudgecontestSpider(scrapy.Spider):
    name = 'vjudgecontest'
    allowed_domains = ['vjudge.csgrandeur.cn']

    def start_requests(self):
        url = LOGIN_URL

        yield scrapy.FormRequest(
            url=url,
            method='POST',
            formdata=LOGIN_FORM_DATA,
            callback=self.parse
        )

    def parse(self, response):
        with open(COOKIE_PATH, 'w+') as file:
            file.write('COOKIE = ' + str(response.headers.get('Set-Cookie')))

        from AcmSpider.config.cookie import COOKIE
        # cookies = {i.split('=')[0]: i.split('=')[1] for i in COOKIE.split('; ')}
        cookies = COOKIE

        def get_group_url(group):
            return VJUDGE_URL + '/group/' + group

        for group in GROUP_LIST:
            yield scrapy.Request(
                url=get_group_url(group),
                method='GET',
                headers={
                    'cookie': cookies,
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35',
                },
                callback=self.get_contest_list
            )

        # yield scrapy.Request(
        #
        # )

    def get_contest_list(self, response):
        with open('test.json', 'w+') as file:
            file.write(response.xpath("//textarea[@name='dataJson']/text()").extract()[0])





