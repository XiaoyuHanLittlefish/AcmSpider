import scrapy
import re

class VjudgecontestSpider(scrapy.Spider):
    name = 'vjudgecontest'
    allowed_domains = ['vjudge.csgrandeur.cn']
    start_urls = ['https://vjudge.csgrandeur.cn']

    def parse(self, response):
        # form_data = {
        #     'login-username': 'XiaoyuHan',
        #     'login-password': 'ybzwanqad'
        # }
        # yield scrapy.FormRequest.from_response(response,
        #     formdata=form_data,callback=self.after_login
        #     ,formid='login-form')
        file_name = 'vjudge.html'
        open(file_name, 'wb+').write(response.body)

    def after_login(self,response):  # 验证是否请求成功
        print(re.findall('Learn Git and GitHub without any code!',response.body.decode()))

