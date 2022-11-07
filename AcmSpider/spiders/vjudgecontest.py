import scrapy
import json

from AcmSpider.config.vjudge.vjudge_config import CONFIG_PATH, LOGIN_URL, LOGIN_FORM_DATA, COOKIE_PATH, GROUP_LIST, VJUDGE_URL


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
        cookies = str(response.headers.get('Set-Cookie'))
        with open(COOKIE_PATH, 'w+') as file:
            file.write('COOKIE = ' + cookies)

        def get_group_url(group_id):
            return VJUDGE_URL + '/group/' + group_id

        for group in GROUP_LIST:
            meta = {
                'group': group,
            }
            yield scrapy.Request(
                url=get_group_url(group),
                method='GET',
                headers={
                    'cookie': cookies,
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35',
                },
                meta=meta,
                callback=self.get_contest_list
            )

    def get_contest_list(self, response):
        contest_list = json.loads(response.xpath(
            "//textarea[@name='dataJson']/text()").extract()[0])['contests']
        with open(CONFIG_PATH + str(response.meta['group']) + '.txt', 'w+') as file:
            file.write(str(contest_list))

        contest_list = [Contest(contest_info) for contest_info in contest_list]


class Contest(object):
    def __init__(self, contest_info):
        contest_id = contest_info[0]
        contest_name = contest_info[1]
        contest_player_num = contest_info[2]
        contest_begin_time = contest_info[3]
        contest_end_time = contest_info[4]
