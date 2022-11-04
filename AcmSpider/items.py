# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CodeforcesItem(scrapy.Item):
    id = scrapy.Field()
    rating = scrapy.Field()
    solve_problem_number = scrapy.Field()


class NowcoderItem(scrapy.Item):
    # id = scrapy.Field()
    name = scrapy.Field()
    rating = scrapy.Field()
    solve_problem_number = scrapy.Field()


class VjudgeContestItem(scrapy.Item):
    class Problem():
        problem_no = 'A'
        problem_name = ''
        is_solved = False
        solved_time = 0
        attempted_time = 0

        def __init__(self, problem_no, problem_name, is_solved, solved_time, attempted_time):
            self.problem_no = problem_no
            self.problem_name = problem_name
            self.is_solved = is_solved
            self.solved_time = solved_time
            self.attempted_time = attempted_time

    class Team():
        name = 'Default Name'
        solved_problem_num = 0
        rank = 0
        score = 0
        penalty = 0
        problems = []

        def __init__(self, name, solved_problem_num, score, penalty):
            self.name = name
            self.solved_problem_num = solved_problem_num
            self.score = score

    teams = scrapy.Field()



