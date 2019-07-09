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
            print("Captcha can't be solved, run spider again...")
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
                callback=self.input_process,
                headers=self.headers,
                dont_filter=True
            )

    def input_process(self, response):
        action = response.xpath('//form[@name="Bkkn001Form"]/@action').extract()[0]
        req_url = urljoin(response.url, action)
        token = response.xpath('//input[@name="org.apache.struts.taglib.html.TOKEN"]/@value').extract()[0]

        self.headers['Referer'] = response.url

        random_id = response.xpath('//input[@id="randomID"]/@value').extract()[0]
        seni_gen_gameen_id = response.xpath('//input[@name="seniGenGamenID"]/@value').extract()[0]

        form_data = {
            'org.apache.struts.taglib.html.TOKEN': token,
            'randomID': random_id,
            'contextPath': '/reins',
            'event': 'forward_searchbabi',
            'bbTtKbn': '1',
            'stateMode': '',
            'stWttBg': '',
            'hzMi': '',
            'zkSyKbn': '2',
            'stJyk': '',
            'bkknShmk1': '',
            'bkknShmk2': '',
            'bkknShbt1': '03',
            'bkknShmkDispList1': '',
            'bkknShmkDispList1': '',
            'bkknShmkDispList1': '',
            'bkknShmkDispList1': '',
            'bkknShmkDispList1': '',
            'bkknShmkDispList1': '',
            'bkknShbt2': '',
            'bkknShmkDispList2': '',
            'bkknShmkDispList2': '',
            'bkknShmkDispList2': '',
            'bkknShmkDispList2': '',
            'bkknShmkDispList2': '',
            'shtkChkKbnShti': '0',
            'shkcknShriSti': '0',
            'shgUmKbn': '1',
            'trhkJyukyu': '0',
            'tdfkMi1': '東京都',
            'shzicmi1_1': '',
            'shzicmi2_1': '',
            'shzicJyk_1': '1',
            'ttmnmi_1': '',
            'ttmnJyk_1': '1',
            'tdfkMi2': '',
            'shzicmi1_2': '',
            'shzicmi2_2': '',
            'shzicJyk_2': '1',
            'ttmnmi_2': '',
            'ttmnJyk_2': '1',
            'tdfkMi3': '',
            'shzicmi1_3': '',
            'shzicmi2_3': '',
            'shzicJyk_3': '1',
            'ttmnmi_3': '',
            'ttmnJyk_3': '1',
            'ensnmi1': '',
            'ekmiFrom1': '',
            'ekmiTo1': '',
            'thNyrkt1': '',
            'thMbKbn1': '',
            'krmKm1': '',
            'bsB1': '',
            'ensnmi2': '',
            'ekmiFrom2': '',
            'ekmiTo2': '',
            'thNyrkt2': '',
            'thMbKbn2': '',
            'krmKm2': '',
            'bsB2': '',
            'ensnmi3': '',
            'ekmiFrom3': '',
            'ekmiTo3': '',
            'thNyrkt3': '',
            'thMbKbn3': '',
            'krmKm3': '',
            'bsB3': '',
            'bsRsmi': '',
            'bsTmiSh': '',
            'tihNyrkt': '',
            'tihMbKbn': '',
            'sotKtu': '',
            'sotKtuNyrkt': '',
            'sotKtuMbKbn': '',
            'kkkuCnryuFrom': '',
            'kkkuCnryuTo': '',
            'siykKkkuCnryuFrom': '',
            'siykKkkuCnryuTo': '',
            'tbTnkFrom': '',
            'tbTnkTo': '',
            'siykTbTnkFrom': '',
            'siykTbTnkTo': '',
            'tcMnskFrom': '',
            'tcMnskTo': '',
            'ttmnMnskFrom': '',
            'ttmnMnskTo': '',
            'snyuMnskFrom': '',
            'snyuMnskTo': '',
            'mdrHysuFrom': '',
            'mdrHysuTo': '',
            'shzikiFrom': '',
            'shzikiTo': '',
            'blcnyHuku': '',
            'stdoHuku': '',
            'stdoJyukyu': '',
            'stdoStmn': '',
            'stdoFkin': '',
            'tskikk': '',
            'yutCik': '',
            'sitkYut': '',
            'ktcJok': '',
            'chushjyuZih': '',
            'cknngtYearFrom': '',
            'cknngtMonthFrom': '',
            'cknngtYearTo': '',
            'cknngtMonthTo': '',
            'kjkrngGgFrom': 'R',
            'kjkrngYearFrom': '',
            'kjkrngMonthFrom': '',
            'kjkrngGgTo': 'R',
            'kjkrngYearTo': '',
            'kjkrngMonthTo': '',
            'optId': '',
            'strStbJok': '',
            'bk1': '',
            'shuhnKnkyu': '',
            'turkKknFlg': '1',
            'turkNngppGgFrom': 'R',
            'turkNngppNenFrom': '',
            'turkNngppGatuFrom': '',
            'turkNngppHiFrom': '',
            'turkNngppGgTo': 'R',
            'turkNngppNenTo': '',
            'turkNngppGatuTo': '',
            'turkNngppHiTo': '',
            'hcKknFlg': '1',
            'hnkuNngppGgFrom': 'R',
            'hnkuNngppNenFrom': '',
            'hnkuNngppGatuFrom': '',
            'hnkuNngppHiFrom': '',
            'hnkuNngppGgTo': 'R',
            'hnkuNngppNenTo': '',
            'hnkuNngppGatuTo': '',
            'hnkuNngppHiTo': '',
            'siykKknFlg': '5',
            'siykNngppGgFrom': 'R',
            'siykNngppNenFrom': '1',
            'siykNngppGatuFrom': '7',
            'siykNngppHiFrom': '1',
            'siykNngppGgTo': 'R',
            'siykNngppNenTo': '1',
            'siykNngppGatuTo': '7',
            'siykNngppHiTo': '2',
            'siykTurkKknFlg': '1',
            'siykTurkNngppGgFrom': 'R',
            'siykTurkNngppNenFrom': '',
            'siykTurkNngppGatuFrom': '',
            'siykTurkNngppHiFrom': '',
            'siykTurkNngppGgTo': 'R',
            'siykTurkNngppNenTo': '',
            'siykTurkNngppGatuTo': '',
            'siykTurkNngppHiTo': '',
            'seniMotFlg': '',
            'seniGenGamenID': seni_gen_gameen_id
        }

        return FormRequest(
            url=req_url,
            method='POST',
            formdata=form_data,
            callback=self.parse_list_page,
            headers=self.headers,
            dont_filter=True
        )

    def parse_list_page(self, response):

        token = response.xpath('//input[@name="org.apache.struts.taglib.html.TOKEN"]/@value').extract()[0]
        random_id = response.xpath('//input[@id="randomID"]/@value').extract()[0]


    def solve_captch_process(self, session_id):

        if self.trying_captcha_solve_count >= 20:
            return

        answer = None

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

        except Exception as e:
            print(e)
            print("captcha can't be solved, retrying now...")
            self.trying_captcha_solve_count += 1
            self.solve_captch_process(session_id)

        if answer:
            print(answer)
            return answer

    @staticmethod
    def _clean_text(text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = re.sub("&nbsp;", " ", text).strip()

        return re.sub(r'\s+', ' ', text)