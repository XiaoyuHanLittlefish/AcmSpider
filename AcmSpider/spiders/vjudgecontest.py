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
        manager_id = contest_datajson['managerId']

        contest = response.meta['contest']
        contest.group_id = response.meta['group'].id
        contest.penalty = penalty
        contest.sum_time = sum_time
        contest.manager_id = manager_id

        db = response.meta['database']
        cursor = db.cursor()
        contest_select_sql = "SELECT * FROM vj_contest WHERE contest_id = %d" % contest.id
        try:
            cursor.execute(contest_select_sql)
            result = cursor.fetchall()
            if result:
                contest_update_sql = \
                    "UPDATE vj_contest SET \
                    contest_name = '%s', \
                    group_id = %d, \
                    player_num = %d, \
                    manager_id = %d, \
                    begin_time = %d, \
                    end_time = %d, \
                    penalty = %d, \
                    sum_time = %d \
                    WHERE contest_id = %d" \
                    % (contest.name, contest.group_id, contest.player_num, contest.manager_id,
                       contest.begin_time, contest.end_time, contest.penalty, contest.sum_time,
                       contest.id)
                try:
                    cursor.execute(contest_update_sql)
                    db.commit()
                except:
                    print('failed to update contest info to mysql')
                    exit(1)
            else:
                contest_insert_sql = "INSERT INTO vj_contest VALUES (%d, '%s', %d, %d, %d, %d, %d, %d, %d)" \
                    % (contest.id, contest.name, contest.group_id, contest.player_num, contest.manager_id,
                       contest.begin_time, contest.end_time, contest.penalty, contest.sum_time)
                try:
                    cursor.execute(contest_insert_sql)
                    db.commit()
                except:
                    print('failed to insert contest info to mysql')
                    exit(1)
        except:
            print('failed to select contest info from mysql')
            exit(1)

        problems = contest_datajson['problems']
        contest.problem_ids = [problem_info['pid']
                               for problem_info in problems]

        contest_problem_select_sql = "SELECT * FROM vj_contest_problem \
                                      WHERE contest_id = %d" \
                                      % (contest.id)
        try:
            cursor.execute(contest_problem_select_sql)
            results = cursor.fetchall()
            contest_problem_ids = [result[0] for result in results]
        except:
            print('failed to select contest problems info from mysql')

        for problem_info in problems:
            problem = Problem(problem_info['pid'], problem_info['title'], problem_info['oj'],
                              problem_info['probNum'], problem_info['num'], problem_info['weight'])
            if problem.id in contest_problem_ids:
                contest_problem_ids.remove(problem.id)
                contest_problem_update_sql = "UPDATE vj_contest_problem SET \
                                              problem_weight = %d" % (problem.weight)
                try:
                    cursor.execute(contest_problem_update_sql)
                    db.commit()
                except:
                    print('failed to update contest problem info to mysql')
                    exit(1)
                continue

            problem_select_sql = "SELECT * FROM vj_problem WHERE problem_id = %d" % problem.id
            try:
                cursor.execute(problem_select_sql)
                result = cursor.fetchall()
                if not result:
                    split_titles = problem.title.split('\'')
                    problem.title = split_titles[0]
                    for i in range(2, len(split_titles)):
                        problem.title = problem.title + '\'' + split_titles[i]
                    problem_insert_sql = "INSERT INTO vj_problem VALUES (%d, '%s', '%s', '%s', '%s')" \
                                         % (problem.id, problem.title, problem.oj, problem.probnum, problem.num)
                    try:
                        cursor.execute(problem_insert_sql)
                        db.commit()
                    except:
                        print('failed to insert problem info to mysql')
                        exit(1)
            except:
                print('failed to select problem info from mysql')
                exit(1)

            contest_problem_insert_sql = "INSERT INTO vj_contest_problem VALUES (%d, %d, %d)" \
                                         % (problem.id, contest.id, problem.weight)
            try:
                cursor.execute(contest_problem_insert_sql)
                db.commit()
            except:
                print('failed to insert contest problem info to mysql')
                exit(1)

        for deleted_problem_id in contest_problem_ids:
            contest_problem_delete_sql = "DELETE FROM vj_contest_problem \
                                          WHERE problem_id = %d AND contest_id = %d" \
                                          % (deleted_problem_id, contest.id)
            try:
                cursor.execute(contest_problem_delete_sql)
                db.commit()
            except:
                print('failed to delete contest problem info from mysql')
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

        contest = response.meta['contest']

        submission_list = [Submission(submission_info)
                           for submission_info
                           in contest_info['submissions']]
        for submission in submission_list:
            submission.contest_id = contest.id
            submission.problem_id = contest.problem_ids[submission.problem_num]
            submission_select_sql = "SELECT * FROM vj_submission \
                                     WHERE user_id = %d AND contest_id = %d AND problem_id = %d" % (
                submission.user_id, submission.contest_id, submission.problem_id)
            try:
                cursor.execute(submission_select_sql)
                result = cursor.fetchall()
                if not result:
                    submission_insert_sql = "INSERT INTO vj_submission VALUES (0, %d, %d, %d, %d, %d)" \
                        % (submission.contest_id, submission.problem_id, submission.user_id,
                           submission.submit_time, submission.is_accepted)
                    try:
                        cursor.execute(submission_insert_sql)
                        db.commit()
                    except:
                        print('failed to insert submission info to mysql')
                        exit(1)
            except:
                print('failed to select submission info from mysql')
                exit(1)


class Group(object):
    def __init__(self, group_id, group_name):
        self.id = group_id
        self.name = group_name


class User(object):
    def __init__(self, user_id, user_info):
        self.id = user_id
        self.username = user_info[0]
        self.nickname = user_info[1]


class Problem(object):
    def __init__(self, problem_id, problem_title, problem_oj, problem_probnum, problem_num, problem_weight):
        self.id = problem_id
        self.title = problem_title
        self.oj = problem_oj
        self.probnum = problem_probnum
        self.num = problem_num
        self.weight = problem_weight


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
