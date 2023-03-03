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

        def get_group_url(group_id):
            return VJUDGE_URL + '/group/' + group_id

        try:
            db = pymysql.connect(host='localhost', port=3306, user='root',
                                 password='root', database='tp6', charset='utf8')
            cursor = db.cursor()
        except:
            print('mysql connection error!')
            exit(1)

        for group_name in GROUP_LIST:
            group_select_sql = "SELECT * FROM vj_group WHERE group_name = '%s'" % group_name
            try:
                cursor.execute(group_select_sql)
                result = cursor.fetchall()
                if result:
                    group = Group(result[0][0], result[0][1])
                else:
                    group_insert_sql = "INSERT INTO vj_group VALUES (0, '%s')" % (
                        group_name)
                    try:
                        cursor.execute(group_insert_sql)
                        group = Group(cursor.lastrowid, group_name)
                        db.commit()
                    except:
                        print('failed to insert group info to mysql')
                        exit(1)
            except:
                print('failed to select group info from mysql')
                exit(1)

            meta = {
                'group': group,
                'cookies': cookies,
                'database': db,
            }
            yield scrapy.Request(
                url=get_group_url(group.name),
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
        with open(CONFIG_PATH + str(response.meta['group'].name) + '.txt', 'w+') as file:
            file.write(str(contest_list))

        contest_list = [Contest(contest_info) for contest_info in contest_list]

        for contest in contest_list:
            meta = {
                'group': response.meta['group'],
                'contest': contest,
                'cookies': response.meta['cookies'],
                'database': response.meta['database'],
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

    def parse_contest(self, response):
        contest_datajson = json.loads(response.xpath(
            "/html/body/textarea/text()").extract()[0])

        penalty = contest_datajson['penalty']
        sum_time = contest_datajson['sumTime']

        contest = response.meta['contest']
        contest.group_id = response.meta['group'].id
        contest.penalty = penalty
        contest.sum_time = sum_time

        db = response.meta['database']
        cursor = db.cursor()
        contest_select_sql = "SELECT * FROM vj_contest WHERE contest_id = %d" % contest.id
        try:
            cursor.execute(contest_select_sql)
            result = cursor.fetchall()
            if result:
                contest_update_sql = "UPDATE vj_contest SET \
                    contest_name = '%s', \
                    group_id = %d, \
                    player_num = %d, \
                    begin_time = %d, \
                    end_time = %d, \
                    penalty = %d, \
                    sum_time = %d \
                    WHERE contest_id = %d" \
                    % (contest.name, contest.group_id, contest.player_num, contest.begin_time,
                       contest.end_time, contest.penalty, contest.sum_time, contest.id)
                try:
                    cursor.execute(contest_update_sql)
                    db.commit()
                except:
                    print('failed to update contest info to mysql')
                    exit(1)
            else:
                contest_insert_sql = "INSERT INTO vj_contest VALUES (%d, '%s', %d, %d, %d, %d, %d, %d)" \
                    % (contest.id, contest.name, contest.group_id, contest.player_num, contest.begin_time,
                        contest.end_time, contest.penalty, contest.sum_time)
                try:
                    cursor.execute(contest_insert_sql)
                    db.commit()
                except:
                    print('failed to insert contest info to mysql')
                    exit(1)
        except:
            print('failed to select contest info from mysql')
            exit(1)

        meta = {
            'group': response.meta['group'],
            'cookies': response.meta['cookies'],
            'database': response.meta['database'],
            'contest': contest,
        }
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

    def parse_contest_rank(self, response):
        # with open(str(response.meta['contest'].contest_id) + '.json', 'wb+') as file:
        #     file.write(response.body)

        contest_info = json.loads(response.body)

        db = response.meta['database']
        cursor = db.cursor()

        user_list = [User(user_id, user_info) 
                     for (user_id, user_info)
                     in contest_info['participants'].items()]
        for user in user_list:
            user.group_id = response.meta['group'].id
            user_select_sql = "SELECT * FROM vj_user WHERE user_id = %s AND group_id = %d" % (
                user.id, user.group_id)
            try:
                cursor.execute(user_select_sql)
                result = cursor.fetchall()
                if result:
                    user_update_sql = "UPDATE vj_user SET \
                        user_name = '%s', \
                        user_nickname = '%s' \
                        WHERE user_id = %s AND group_id = %d" \
                        % (user.username, user.nickname, user.id, user.group_id)
                    try:
                        cursor.execute(user_update_sql)
                        db.commit()
                    except:
                        print('failed to update user info to mysql')
                        exit(1)
                else:
                    user_insert_sql = "INSERT INTO vj_user VALUES (%s, %d, '%s', '%s')" \
                        % (user.id, user.group_id, user.username, user.nickname)
                    try:
                        cursor.execute(user_insert_sql)
                        db.commit()
                    except:
                        print('failed to insert user info to mysql')
                        exit(1)
            except:
                print('failed to select user info from mysql')
                exit(1)

        submission_list = [Submission(submission_info)
                           for submission_info
                           in contest_info['submissions']]


class Group(object):
    def __init__(self, group_id, group_name):
        self.id = group_id
        self.name = group_name


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
        self.id = contest_info[0]
        self.name = contest_info[1]
        self.player_num = contest_info[2]
        self.begin_time = contest_info[3]
        self.end_time = contest_info[4]

    def url(self):
        return 'https://vjudge.csgrandeur.cn/contest/' + str(self.id)

    def rank_url(self):
        return 'https://vjudge.csgrandeur.cn/contest/rank/single/' + str(self.id)
