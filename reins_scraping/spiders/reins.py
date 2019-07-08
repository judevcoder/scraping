import re
import scrapy
import requests
import urllib.request

from PIL import Image
# from urlparse import urljoin
from lxml import html

#
# class StateFarmItem(scrapy.Item):
#     Name = scrapy.Field()
#     Address = scrapy.Field()
#     City = scrapy.Field()
#     Phone_number = scrapy.Field()
#


class RenisSpider(scrapy.Spider):

    name = 'reins'

    allowed_domains = ["system.reins.jp"]

    start_urls = ['https://system.reins.jp/reins/ktgyoumu/KG001_001.do']

    user_id = '302336607294'

    password = 'marube'

    api_key = 'c81d01b13adbec52d5213925cad16baa'

    captcha_req_url = 'http://2captcha.com/in.php'

    captcha_res_url = 'http://2captcha.com/res.php'

    captcha_image = 'https://system.reins.jp/reins/ktgyoumu/KG001_001JcaptchaAction.do'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/41.0.2228.0 Safari/537.36', }

    def __init__(self, *args, **kwargs):
        super(RenisSpider, self).__init__(site_name=self.allowed_domains[0], *args, **kwargs)
        self.current_page = 0

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.login_process, headers=self.headers)

    def login_process(self, response):
        with urllib.request.urlopen(self.captcha_image) as url:
            with open('temp.jpg', 'wb') as f:
                f.write(url.read())

        # img = Image.open('temp.jpg')

        files = {'file': open('temp.jpg', 'rb')}
        data = {'key': self.api_key, 'method': 'post'}

        s = requests.Session()

        captcha_id = s.post(self.captcha_req_url, files=files, data=data).text.split('|')[1]

        answer = s.get(self.captcha_res_url + '?key={}&action=get&id={}'.format(self.api_key, captcha_id)).text.split('|')[1]

    @staticmethod
    def _clean_text(text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = re.sub("&nbsp;", " ", text).strip()

        return re.sub(r'\s+', ' ', text)