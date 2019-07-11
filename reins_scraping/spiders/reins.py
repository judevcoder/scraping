import re
import time
import scrapy
import requests
import urllib.request

from lxml import html
from urllib.parse import urljoin, urlencode
from scrapy.http import Request, FormRequest

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

    detail_page_index = 1

    list_count_per_page = 0

    total_count = 0

    next_page = False

    def __init__(self, *args, **kwargs):
        super(RenisSpider, self).__init__(site_name=self.allowed_domains[0], *args, **kwargs)
        self.current_page = 1

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.login_process)

    def login_process(self, response):

        action_link = response.xpath('//form[@name="TT_UsrForm"]/@action').extract()[0]
        jsession_id = re.search(';jsessionid(.*?)?r', action_link)
        if jsession_id:
            jsession_id = jsession_id.group(0).replace(';jsessionid=', '').replace('?r', '')
            url = urljoin(response.url, action_link.replace(jsession_id, '').replace(';jsessionid=', ''))
            self.headers['Cookie'] = 'JSESSIONID={session_id}; currentUserid={user_id}' \
                .format(session_id=jsession_id, user_id=self.user_id)
        else:
            url = urljoin(response.url, action_link)

        html_token = response.xpath('//input[@name="org.apache.struts.taglib.html.TOKEN"]/@value').extract()[0]

        captcha_answer = self.solve_captcha_process()

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

        return FormRequest(
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
            'siykNngppHiTo': '5',
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

        url = urljoin(response.url, response.xpath('//form[@name="Bkkn002Form"]/@action').extract()[0])

        senigengamen_id = response.xpath('//input[@name="seniGenGamenID"]/@value').extract()[0]
        sne_id = response.xpath('//input[@name="sneId"]/@value').extract()[0]

        self.headers['Referer'] = response.url

        if '次へ' in response.body_as_unicode():
            self.next_page = True
        else:
            self.next_page = False

        form_data = {
            'org.apache.struts.taglib.html.TOKEN': token,
            'randomID': random_id,
            'contextPath': '/reins',
            'selectedOrderItem1': '',
            'selectedOrderItem2': '',
            'shugu': '1',
            'dtShri': '02',
            'bkknId': '',
            'shgUmKbn': '1',
            'sneId': sne_id,
            'listBngu': '1',
            'printMode': 'off',
            'sortMode': 'off',
            'seniMotFlg': '',
            'bkknIdList': '',
            'seniGenGamenID': senigengamen_id,
            'modoruBkknId': '',
            'row1': '50',
            'startIndex1': '0',
            'event': 'forward_syousei',
            'bkknBngu1': '100097346915',
            'bkknBngu1': '100097597818',
            'bkknBngu1': '100097696500',
            'bkknBngu1': '100097775709',
            'bkknBngu1': '100097971545',
            'bkknBngu1': '100098042625',
            'bkknBngu1': '100098406288',
            'bkknBngu1': '100098606676',
            'bkknBngu1': '100099183594',
            'bkknBngu1': '100099242129',
            'bkknBngu1': '100099332858',
            'bkknBngu1': '100099498604',
            'bkknBngu1': '100099513364',
            'bkknBngu1': '100099565136',
            'bkknBngu1': '100099572180'
        }

        if self.detail_page_index > self.list_count_per_page:
            if self.next_page:

                next_page_url = response.url
                next_page_form_data = {
                    'org.apache.struts.taglib.html.TOKEN': token,
                    'randomID': random_id,
                    'contextPath': '/reins',
                    'selectedOrderItem1': '',
                    'selectedOrderItem2': '',
                    'shugu': '',
                    'dtShri': '',
                    'bkknId': '',
                    'shgUmKbn': '1',
                    'sneId': sne_id,
                    'listBngu': '',
                    'printMode': 'off',
                    'sortMode': 'off',
                    'seniMotFlg': '',
                    'bkknIdList': '',
                    'seniGenGamenID': senigengamen_id,
                    'modoruBkknId': '',
                    'row1': '50',
                    'startIndex1': str(self.current_page * 50),
                    'event': 'forward_pageLinks',
                    'bkknBngu1': '100091554338',
                    'bkknBngu1': '100092135843',
                    'bkknBngu1': '100095381738',
                    'bkknBngu1': '100095765372',
                    'bkknBngu1': '100095944967',
                    'bkknBngu1': '100096112920',
                    'bkknBngu1': '100096377623',
                    'bkknBngu1': '100096471809',
                    'bkknBngu1': '100097046892',
                    'bkknBngu1': '100097068089',
                    'bkknBngu1': '100097346915',
                    'bkknBngu1': '100097389594',
                    'bkknBngu1': '100097395285',
                    'bkknBngu1': '100097440712',
                    'bkknBngu1': '100097597818',
                    'bkknBngu1': '100097696500',
                    'bkknBngu1': '100097760004',
                    'bkknBngu1': '100097775709',
                    'bkknBngu1': '100097971545',
                    'bkknBngu1': '100097977705',
                    'bkknBngu1': '100098042625',
                    'bkknBngu1': '100098112308',
                    'bkknBngu1': '100098307211',
                    'bkknBngu1': '100098355518',
                    'bkknBngu1': '100098406288',
                    'bkknBngu1': '100098451478',
                    'bkknBngu1': '100098559286',
                    'bkknBngu1': '100098590072',
                    'bkknBngu1': '100098606676',
                    'bkknBngu1': '100098659834',
                    'bkknBngu1': '100098734439',
                    'bkknBngu1': '100098760221',
                    'bkknBngu1': '100098900286',
                    'bkknBngu1': '100098971374',
                    'bkknBngu1': '100099129902',
                    'bkknBngu1': '100099146393',
                    'bkknBngu1': '100099183594',
                    'bkknBngu1': '100099190697',
                    'bkknBngu1': '100099195510',
                    'bkknBngu1': '100099218489',
                    'bkknBngu1': '100099242129',
                    'bkknBngu1': '100099289819',
                    'bkknBngu1': '100099300864',
                    'bkknBngu1': '100099323036',
                    'bkknBngu1': '100099323925',
                    'bkknBngu1': '100099332858',
                    'bkknBngu1': '100099350991'
                }
                self.current_page += 1
                self.detail_page_index = 1
                return FormRequest(
                    url=next_page_url,
                    method='POST',
                    formdata=next_page_form_data,
                    callback=self.parse_list_page,
                    headers=self.headers,
                    dont_filter=True
                )
            else:
                return

        table_tr = response.xpath('//table[@class="innerTable"]/tr').extract()
        if self.detail_page_index == 1:
            self.list_count_per_page = len(table_tr)
            self.total_count = int(response.xpath('//a[@href="#tochi"]/text()')
                                   .extract()[0].replace('売マンション(', '').replace('件)', ''))

        bkknld = html.fromstring(table_tr[self.detail_page_index]).xpath(
            '//input[@src="/reins/img/btn_detail.gif"]/@id')[0].replace('_', '')
        if len(bkknld):
            form_data['bkknId'] = bkknld
            return FormRequest(
                url=url,
                method='POST',
                formdata=form_data,
                callback=self.parse_detail_page,
                headers=self.headers,
                dont_filter=True
            )

    def parse_detail_page(self, response):
        print('Detail Index - ', self.detail_page_index)
        self.detail_page_index += 1
        print('Next Page - ', self.next_page)
        print('Current Page - ', self.current_page)
        print('List Count - ', self.list_count_per_page)
        print('Total Count - ', self.total_count)

        number = response.xpath('//p[@class="shirotoMsg"]/span/text()').extract()[0].replace('物件番号：', '')
        params = re.search('openPdfDownLoad(.*?)value', response.body_as_unicode())
        if params:
            params = params.group(0).replace("'", "").split(',')
            url = params[0].replace('openPdfDownLoad(', '')
            bkkn_id = params[1]
            r = params[2]
            download_link = 'https://system.reins.jp{url}?bkknId={bkkn_id}&kduFlg=1&knskFlg=1&r={r}'.format(
                url=url,
                bkkn_id=bkkn_id,
                r=r
            )
            r = requests.get(download_link, headers=self.headers, allow_redirects=False)
            with open('{name}.pdf'.format(name=number), 'wb') as f:
                f.write(r.content)

        back_link = urljoin(response.url, response.xpath('//form[@name="BkknForm"]/@action').extract()[0])

        token = response.xpath('//input[@name="org.apache.struts.taglib.html.TOKEN"]/@value').extract()
        token = token[0] if token else ''

        random_id = response.xpath('//input[@name="randomID"]/@value').extract()
        random_id = random_id[0] if random_id else ''

        dtshri = response.xpath('//input[@name="dtShri"]/@value').extract()
        dtshri = dtshri[0] if dtshri else ''

        qbkkn_id = response.xpath('//input[@name="qbkknId"]/@value').extract()
        qbkkn_id = qbkkn_id[0] if qbkkn_id else ''

        hbkkn_id = response.xpath('//input[@name="hbkknId"]/@value').extract()
        hbkkn_id = hbkkn_id[0] if hbkkn_id else ''

        fomr_data_bkkn_id = response.xpath('//input[@name="bkknId"]/@value').extract()
        fomr_data_bkkn_id = fomr_data_bkkn_id[0] if fomr_data_bkkn_id else ''

        shugu = response.xpath('//input[@name="shugu"]/@value').extract()
        shugu = shugu[0] if shugu else ''

        btnxkx = response.xpath('//input[@name="btnxkx"]/@value').extract()
        btnxkx = btnxkx[0] if btnxkx else ''

        print_mode = response.xpath('//input[@name="printMode"]/@value').extract()
        print_mode = print_mode[0] if print_mode else ''

        knskflg = response.xpath('//input[@name="knskFlg"]/@value').extract()
        knskflg = knskflg[0] if knskflg else ''

        zmnflmi = response.xpath('//input[@name="zmnFlmi"]/@value').extract()
        zmnflmi = zmnflmi[0] if zmnflmi else ''

        sne_id = response.xpath('//input[@name="sneId"]/@value').extract()
        sne_id = sne_id[0] if sne_id else ''

        seni_gen_gamen_id = response.xpath('//input[@name="seniGenGamenID"]/@value').extract()
        seni_gen_gamen_id = seni_gen_gamen_id[0] if seni_gen_gamen_id else ''

        modorubkkn_id = response.xpath('//input[@name="modoruBkknId"]/@value').extract()
        modorubkkn_id = modorubkkn_id[0] if modorubkkn_id else ''

        form_data = {
            'org.apache.struts.taglib.html.TOKEN': token,
            'randomID': random_id,
            'contextPath': '/reins',
            'dtShri': dtshri,
            'qbkknId': qbkkn_id,
            'hbkknId': hbkkn_id,
            'bkknId': fomr_data_bkkn_id,
            'shugu': shugu,
            'btnxkx': btnxkx,
            'printMode': print_mode,
            'event': 'forward_search',
            'knskFlg': knskflg,
            'zmnFlmi': zmnflmi,
            'sneId': sne_id,
            'seniGenGamenID': seni_gen_gamen_id,
            'modoruBkknId': modorubkkn_id
        }

        return FormRequest(
            url=back_link,
            method='POST',
            formdata=form_data,
            callback=self.parse_list_page,
            headers=self.headers,
            dont_filter=True
        )

    def solve_captcha_process(self):
        answer = None

        for i in range(20):
            if answer:
                return answer

            try:

                self.headers['Accept'] = 'image/webp,image/apng,image/*,*/*;q=0.8'

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

    @staticmethod
    def _clean_text(text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        text = re.sub("&nbsp;", " ", text).strip()

        return re.sub(r'\s+', ' ', text)