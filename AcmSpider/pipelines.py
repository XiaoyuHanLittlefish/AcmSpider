# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymysql
from itemadapter import ItemAdapter


class AcmspiderPipeline:
    def __init__(self):
        pass
        # self.db = pymysql.connect(host='localhost', port=3306, user='root', password='root', database='tp6', charset='utf8')
        # self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        pass
        # return item

    def close_spider(self, spider):
        pass
        # self.cursor.close()
        # self.db.close()
