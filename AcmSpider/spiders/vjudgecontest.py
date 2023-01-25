# -*- coding: utf-8 -*-
import scrapy
import json
import pymysql

from AcmSpider.config.vjudge.vjudge_config import CONFIG_PATH, LOGIN_URL, LOGIN_FORM_DATA, COOKIE_PATH, GROUP_LIST, \
    VJUDGE_URL


class VjudgecontestSpider(scrapy.Spider):
    name = 'vjudgecontest'
    allowed_domains = ['vjudge.csgrandeur.cn']

    def start_requests(self):
        url = LOGIN_URL

        yield scrapy.FormRequest(
            url=url,
            method='POST',
            formdata=LOGIN_FORM_DATA,
            callback=self.parse_group
        )

    def parse_group(self, response):
        cookies = str(response.headers.get('Set-Cookie'))
        with open(COOKIE_PATH, 'w+') as file:
            file.write('COOKIE = ' + cookies)
        def get_group_url(group_id):
            return VJUDGE_URL + '/group/' + group_id

        for group in GROUP_LIST:
            meta = {
                'group': group,
                'cookies': cookies
            }
            yield scrapy.Request(
                url=get_group_url(group),
                method='GET',
                headers={
                    'cookie': cookies,
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76',
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

        for contest in contest_list:
            meta = {
                'contest': contest,
            }
            # 获取contest的设置
            contest_url = contest.url()
            yield scrapy.Request(
                url=contest_url,
                method='GET',
                headers={
                    'cookie': response.meta['cookies'],
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76',
                },
                meta=meta,
                callback=self.parse_contest
            )
            # 获取contest的rank
            contest_rank_url = contest.rank_url()
            yield scrapy.Request(
                url=contest_rank_url,
                method='GET',
                headers={
                    'cookie': response.meta['cookies'],
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76',
                },
                meta=meta,
                callback=self.parse_contest_rank
            )


    def parse_contest(self, response):
        contest_datajson = json.loads(response.xpath("/html/body/textarea/text()").extract()[0])

        penalty = contest_datajson['penalty']
        sum_time = contest_datajson['sumTime']

        response.meta['penalty'] = penalty
        response.meta['sum_time'] = sum_time

    def parse_contest_rank(self, response):
        with open(str(response.meta['contest'].contest_id) + '.json', 'wb+') as file:
            file.write(response.body)

        contest = json.loads(response.body)

        user_list = [User(user_id, user_info) for (user_id, user_info) in contest['participants'].items()]
        submission_list = [Submission(submission_info) for submission_info in contest['submissions']]

        print(response.meta)


class User(object):
    def __init__(self, user_id, user_info):
        self.id = user_id
        self.username = user_info[0]
        self.nickname = user_info[1]


class Submission(object):
    def __init__(self, submission_info):
        self.user_id = submission_info[0]
        self.problem_num = submission_info[1]
        self.is_accepted = submission_info[2]
        self.submit_time = submission_info[3]


class Contest(object):
    def __init__(self, contest_info):
        self.contest_id = contest_info[0]
        self.contest_name = contest_info[1]
        self.contest_player_num = contest_info[2]
        self.contest_begin_time = contest_info[3]
        self.contest_end_time = contest_info[4]

    def url(self):
        return 'https://vjudge.csgrandeur.cn/contest/' + str(self.contest_id)

    def rank_url(self):
        return 'https://vjudge.csgrandeur.cn/contest/rank/single/' + str(self.contest_id)
