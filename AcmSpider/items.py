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
