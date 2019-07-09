import re
import time
import scrapy
import requests
import urllib.request

from urllib.parse import urljoin, urlencode
from scrapy.http import Request, FormRequest

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

    headers = {
        'Accept': '',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': '',
        'Host': 'system.reins.jp',
        'Referer': 'https: // system.reins.jp / reins / ktgyoumu / KG001_001.do',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/75.0.3770.100 Safari/537.36'
    }

    trying_captcha_solve_count = 1

    def __init__(self, *args, **kwargs):
        super(RenisSpider, self).__init__(site_name=self.allowed_domains[0], *args, **kwargs)
        self.current_page = 0

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.login_process)

    def login_process(self, response):

        action_link = response.xpath('//form[@name="TT_UsrForm"]/@action').extract()[0]
        jsession_id = re.search(';jsessionid(.*?)?r', action_link).group(0).replace(';jsessionid=', '').replace('?r', '')

        url = urljoin(response.url, action_link.replace(jsession_id, '').replace(';jsessionid=', ''))

        html_token = response.xpath('//input[@name="org.apache.struts.taglib.html.TOKEN"]/@value').extract()[0]

        captcha_answer = self.solve_captch_process(jsession_id)

        if captcha_answer:
            print("captcha solved")
        else:
            print("Ca[tcha didn't solve")
            return

        self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,ima'

        form_data = {
            'org.apache.struts.taglib.html.TOKEN': html_token,
            'usrId': self.user_id,
            'inpswrd': self.password,
            'kywrd': captcha_answer
        }

        yield FormRequest(
            url=url,
            method='POST',
            formdata=form_data,
            callback=self.after_login,
            dont_filter=True
        )

    def after_login(self, response):
        if response.xpath('//span[@id="logout"]'):
            print("logged in successfully")

        token = response.xpath('//input[@name="org.apache.struts.taglib.html.TOKEN"]/@value').extract()[0]

        form_data = {
            'org.apache.struts.taglib.html.TOKEN': token,
            'ybdshShrKbn': '6',
            'x': '88',
            'y': '22'
        }

        self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,' \
                                 '*/*;q=0.8,application/signed-exchange;v=b3'
        sale_url = None

        # urls = urljoin(response.url, response.xpath('//form[@name="TT_UsrForm"]/@action').extract())
        urls = response.xpath('//form[@name="TT_UsrForm"]/@action').extract()
        for url in urls:
            if 'BK001_001.do?r' in url:
                sale_url = urljoin(response.url, url)
                break

        self.headers['Referer'] = response.url

        if sale_url:
            return FormRequest(
                url=sale_url,
                method='POST',
                formdata=form_data,
                callback=self.parse_list_page,
                headers=self.headers,
                dont_filter=True
            )

    def parse_list_page(self, response):
        res = response

    def solve_captch_process(self, session_id):

        if self.trying_captcha_solve_count >= 10:
            return

        try:
            self.headers['Accept'] = 'image/webp,image/apng,image/*,*/*;q=0.8'
            self.headers['Cookie'] = 'JSESSIONID={session_id}; currentUserid={user_id}'\
                .format(session_id=session_id, user_id=self.user_id)

            print("trying to solve captcha")

            r = requests.get(self.captcha_image, headers=self.headers, allow_redirects=False)
            with open('temp.jpg', 'wb') as f:
                f.write(r.content)

            files = {'file': open('temp.jpg', 'rb')}
            data = {'key': self.api_key, 'method': 'post'}

            s = requests.Session()

            captcha_id = s.post(self.captcha_req_url, files=files, data=data).text.split('|')[1]
            time.sleep(10)

            answer = s.get(self.captcha_res_url + '?key={}&action=get&id={}'.format(self.api_key, captcha_id)).text.split('|')[1]
            time.sleep(10)

            return answer

        except Exception as e:
            print(e)
            print("captcha can't be solved, retrying now...")
            self.trying_captcha_solve_count += 1
            self.solve_captch_process(session_id)

    @staticmethod
    def _clean_text(text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = re.sub("&nbsp;", " ", text).strip()

        return re.sub(r'\s+', ' ', text)