import re
import os
import time
import scrapy
import requests

from lxml import html
from urllib.parse import urljoin
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

        bkknBngu1_list = response.xpath('//input[@name="bkknBngu1"]/@value').extract()

        row1 = response.xpath('//input[@name="row1"]/@value').extract()
        row1 = row1[0] if row1 else ''

        start_index = response.xpath('//input[@name="startIndex1"]/@value').extract()
        start_index = start_index[0] if start_index else ''

        self.headers['Referer'] = response.url

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
            'row1': row1,
            'startIndex1': start_index,
            'event': 'forward_syousei',
            'bkknBngu1': bkknBngu1_list
        }

        table_tr = response.xpath('//table[@class="innerTable"]/tr').extract()
        if self.detail_page_index == 1:
            self.list_count_per_page = len(table_tr)
            self.total_count = int(response.xpath('//a[@href="#tochi"]/text()')
                                   .extract()[0].replace('売マンション(', '').replace('件)', ''))
            if response.xpath('///a[text()="次へ"]'):
                self.next_page = True
            else:
                self.next_page = False
        if self.detail_page_index >= self.list_count_per_page:
            if self.next_page:

                next_page_url = urljoin(response.url, response.xpath('//form[@name="Bkkn002Form"]/@action').extract()[0])

                selectedOrderItem1 = response.xpath('//input[@name="selectedOrderItem1"]/@value').extract()
                selectedOrderItem1 = selectedOrderItem1[0] if selectedOrderItem1 else ''

                selectedOrderItem2 = response.xpath('//input[@name="selectedOrderItem2"]/@value').extract()
                selectedOrderItem2 = selectedOrderItem2[0] if selectedOrderItem2 else ''

                shugu = response.xpath('//input[@name="shugu"]/@value').extract()
                shugu = shugu[0] if shugu else ''

                dtShri = response.xpath('//input[@name="dtShri"]/@value').extract()
                dtShri = dtShri[0] if dtShri else ''

                bkknId = response.xpath('//input[@name="bkknId"]/@value').extract()
                bkknId = bkknId[0] if bkknId else ''

                shgUmKbn = response.xpath('//input[@name="shgUmKbn"]/@value').extract()
                shgUmKbn = shgUmKbn[0] if shgUmKbn else ''

                listBngu = response.xpath('//input[@name="listBngu"]/@value').extract()
                listBngu = listBngu[0] if listBngu else ''

                printMode = response.xpath('//input[@name="printMode"]/@value').extract()
                printMode = printMode[0] if printMode else ''

                sortMode = response.xpath('//input[@name="sortMode"]/@value').extract()
                sortMode = sortMode[0] if sortMode else ''

                seniMotFlg = response.xpath('//input[@name="seniMotFlg"]/@value').extract()
                seniMotFlg = seniMotFlg[0] if seniMotFlg else ''

                bkknIdList = response.xpath('//input[@name="bkknIdList"]/@value').extract()
                bkknIdList = bkknIdList[0] if bkknIdList else ''

                modoruBkknId = response.xpath('//input[@name="modoruBkknId"]/@value').extract()
                modoruBkknId = modoruBkknId[0] if modoruBkknId else ''

                next_page_form_data = {
                    'org.apache.struts.taglib.html.TOKEN': token,
                    'randomID': random_id,
                    'contextPath': '/reins',
                    'selectedOrderItem1': selectedOrderItem1,
                    'selectedOrderItem2': selectedOrderItem2,
                    'shugu': shugu,
                    'dtShri': dtShri,
                    'bkknId': bkknId,
                    'shgUmKbn': shgUmKbn,
                    'sneId': sne_id,
                    'listBngu': listBngu,
                    'printMode': printMode,
                    'sortMode': sortMode,
                    'seniMotFlg': seniMotFlg,
                    'bkknIdList': bkknIdList,
                    'seniGenGamenID': senigengamen_id,
                    'modoruBkknId': modoruBkknId,
                    'row1': '50',
                    'startIndex1': str(self.current_page * 50),
                    'event': 'forward_pageLinks',
                    'bkknBngu1': bkknBngu1_list
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
                print("Crawling done. Closing spider...")
                return

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
        print('List Index - ', self.detail_page_index + (self.current_page - 1) * 50)
        self.detail_page_index += 1
        print('Next Page - ', self.next_page)
        print('Current Page - ', self.current_page)
        print('List Count per page- ', self.list_count_per_page - 1)
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

            if not os.path.exists('download'):
                os.makedirs('download')

            with open('download/{name}.pdf'.format(name=number), 'wb') as f:
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
                with open('captcha.jpg', 'wb') as f:
                    f.write(r.content)

                files = {'file': open('captcha.jpg', 'rb')}
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