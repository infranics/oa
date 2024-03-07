from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pyperclip
import logging
import requests
import json
import random
import config
from urllib import parse
from time import localtime, strftime
# from hospital import Hospital

import threading

#
# env info
#

# log
logging.basicConfig(filename='%s\\sylvan.log' % config.CONFIG['home_dir'],
                    level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(message)s')

logging.Formatter(datefmt='%m-%d,%H:%M:%S.%f')


#
# functions
#

# 전체 병원 정보 가져옴
def get_rest_vaccine_info():
    logger = logging.getLogger("get_rest_vaccine_info")

    try:
        url = "https://api.place.naver.com/graphql"
        # logger.info("request :\n%s" % url)

        with open('%s\\data.json' % config.CONFIG['home_dir'], 'r', encoding="UTF-8") as f:
            json_data = f.readline().encode("utf-8")

        headers = {'Content-type': 'application/json'}

        # logger.info("send request :\n%s" % json_data)
        resp = requests.post(url, data=json_data, headers=headers)

        # logger.info("response status: %d" % resp.status_code);
        # logger.info("response body:\n%s" % resp.text);

        resp_json_data = json.loads(resp.text)

        return resp_json_data

    except Exception as ex:
        logger.info("get_rest_vaccine_info 실패: %s " % ex)


# 전체 병원 정보 가져옴
def get_rest_vaccine_info2(driver):
    logger = logging.getLogger("get_rest_vaccine_info")

    try:
        url = "https://api.place.naver.com/graphql"
        # logger.info("request :\n%s" % url)

        with open('%s\\data.json' % config.CONFIG['home_dir'], 'r', encoding="UTF-8") as f:
            json_data = f.readline().encode("utf-8")

        headers = {'Content-type': 'application/json',
                   'cookie': '%s' % driver.get_cookies(),
                   'origin': 'https://m.place.naver.com',
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'}

        # logger.info("send request :\n%s" % json_data)
        resp = requests.post(url, data=json_data, headers=headers)

        # logger.info("response status: %d" % resp.status_code);
        # logger.info("response body:\n%s" % resp.text);

        resp_json_data = json.loads(resp.text)

        return resp_json_data

    except Exception as ex:
        logger.info("get_rest_vaccine_info 실패: %s " % ex)


# 전체병원정보에서 백신이 있는 곳이 있으면 반환
def find_rest_vaccine(rest_json_data):
    logger = logging.getLogger("find_rest_vaccine")

    item = {}
    check_count = 0

    try:
        json_array = rest_json_data[0].get("data").get('rests').get('businesses').get('items')

        # pprint.pprint(json_array)

        for item in json_array:

            check_count = check_count + 1

            vaccine_quantity = item.get('vaccineQuantity')

            if vaccine_quantity is None:
                continue

            total_quantity = vaccine_quantity.get('totalQuantity')

            # 백신이 1개이상이면 반환, 나중에 백신종류도 조건에 넣을것
            if total_quantity > 0:  # and vaccine_type == "화이자":
                logger.info("vaccine available : \n %s" % item)

                return item, check_count

    except Exception as ex:
        logger.info("find_rest_vaccine 실패: %s " % ex)
        logger.info("find_rest_vaccine 실패: %s " % rest_json_data)

    return {}, check_count
    # 테스트용으로 마지막 병원 리턴
    # return item


# 네이버 로그인
def login_naver():
    logger = logging.getLogger("login_naver")
    try:
        # 기본 브라우저 프로필 가져오기, 없으면 계속 브라우저 등록하라고 뜸.

        if config.CONFIG['browser'] == 'chrome':

            #
            # naver에서 navigator.webdriver 채크함. 아래 옵션으로 navigator.webdriver 채크 피하기
            #

            options = webdriver.ChromeOptions()
            options.add_argument("user-data-dir=C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data")

            # options.add_argument("start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-blink-features=AutomationControlled")
            # browser 표시 여부, browser 띄우면 병원페이지 0.5초 예약페이지 0.5초 걸림
            # options.add_argument("--headless");

            # naver 로그인
            driver = webdriver.Chrome(options=options)

            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/83.0.4103.53 Safari/537.36'})
            logger.info(driver.execute_script("return navigator.userAgent;"))




        elif config.CONFIG['browser'] == 'firefox':
            fp = webdriver.FirefoxProfile('C:\\Users\\user\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles'
                                          '\\2cyrg3xs.default-release')
            driver = webdriver.Firefox(firefox_profile=fp)

        driver.get('https://nid.naver.com/nidlogin.login')

        # id, pw 입력할 곳을 찾습니다.
        tag_id = driver.find_element_by_name('id')
        tag_pw = driver.find_element_by_name('pw')
        tag_id.clear()
        time.sleep(1)

        # id 입력
        tag_id.click()
        tag_id.clear()
        pyperclip.copy(config.CONFIG['naver_id'])
        tag_id.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        # pw 입력
        tag_pw.click()
        tag_pw.clear()
        pyperclip.copy(config.CONFIG['naver_pw'])
        tag_pw.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        # 로그인 버튼을 클릭합니다
        login_btn = driver.find_element_by_id('log.login')
        login_btn.click()

        # 잔여백신으로 이동

        time.sleep(1)

        #       목동
        #        driver.get('https://m.place.naver.com/rest/vaccine?vaccineFilter=used'
        #                   '&x=126.8920805&y=37.4941623&bounds=126.7565539%3B37.4477041%3B127.0276072%3B37.5405917')

        # driver.get('https://m.place.naver.com/rest/vaccine?vaccineFilter=used'
        #           '&x=129.0822045&y=35.176542&bounds=128.9889924%3B35.1441233%3B129.1754167%3B35.2089478')

        driver.get('https://m.place.naver.com/rest/vaccine?vaccineFilter=used'
                   '&x=%s&y=%s&bounds=%s' % (config.CONFIG['x'], config.CONFIG['y'], config.CONFIG['bounds']))

        time.sleep(1)

        return driver

    except Exception as ex:
        logger.info("login_naver 실패: %s " % ex)


# 백신을 가지고 있는 병원을 네이버잔여백신에서 접종예약신청
def register_rest_vaccine(json_item, driver):
    logger = logging.getLogger("register_rest_vaccine")
    try:

        # logger.info("register_rest_vaccine:잔여백신 등록 시작")

        # reservation parameter
        sid = json_item.get('id')
        orgcd = json_item.get('vaccineQuantity').get('vaccineOrganizationCode')

        # 병원 페이지 url
        register_url = "https://v-search.nid.naver.com/reservation?orgCd=%s&sid=%s" % (orgcd, sid)

        driver.get(register_url)

        logger.info("register_rest_vaccine:잔여백신 예약신청 페이지: %s" % register_url)

        #
        # 예약 페이지 이동후 직행
        #
        # 개인정보 수집 동의가 있으면 진행
        """
        try:
            logger.info("register_rest_vaccine:개인동의필드 체크 시도")
            agree_btn = driver.find_element_by_xpath("//label[@for='check_all']")

            if agree_btn is not None:
                driver.execute_script("arguments[0].click();", agree_btn)
                logger.info("register_rest_vaccine: check agree all")
        except Exception as ex:
            logger.info("register_rest_vaccine:개인동의필드없음: %s " % ex)
        """

        """
        # 화이자 백선 수량 선택
        logger.info("register_rest_vaccine:잔여백신 선택")

        # select_btn = driver.find_element_by_xpath("//label[@for='VEN00013']")
        select_btn = driver.find_element_by_id("VEN00013")

        # driver.find_element_by_id("questionaire3").send_keys ('Value One')

        # select_btn = driver.find_element_by_css_selector("input#id_gender1").click()

        if select_btn is not None and select_btn.is_selected() is False:
            # select_btn.click()

            for i in range(1, 5):
                select_btn.click()
                # driver.execute_script("arguments[0].click();", select_btn)

                if select_btn.is_selected() is False:
                    time.sleep(1)
                else:
                    break

            logger.info("register_rest_vaccine: check vaccine is selected : %s" % select_btn.is_selected())

            # change as it says
            # infobox_div = driver.find_element_by_xpath("//div[contains(@class,'info_box on')]")
            # driver.execute_script("arguments[0].setAttribute('class','info_box off')", infobox_div)

        else:
            logger.info(
                "register_rest_vaccine: fail to click vaccine : check vaccine is selected :%s" % select_btn.is_selected())
        """

        # logger.info("register_rest_vaccine:예약신청")

        #
        # key cd
        #
        """
        key = driver.find_element_by_id("key").get_attribute("value")
        # cd = select_btn.get_attribute("cd")
        cd = 'VEN00013'
        href = "/reservation/progress?key=%s&cd=%s" % (key, cd)

        # 제대로 안될경우 바로 reservation 사이트 이동
        driver.get('https://v-search.nid.naver.com%s' % href)

        # driver.execute_script("arguments[0].setAttribute('class','link_confirm on')", confirm_btn)
        # driver.execute_script("arguments[0].setAttribute('href','%s')" % href, confirm_btn)
        # logger.info("register_rest_vaccine: windows.location.href = %s" % href)
        # driver.execute_script('window.location.href = "{}";'.format(href))

        """

        # 예약신청
        # logger.info("register_rest_vaccine: find confirm button")
        confirm_btn = driver.find_element_by_id("reservation_confirm")

        # logger.info("register_rest_vaccine: click confirm button")
        # driver.execute_script("arguments[0].click();", confirm_btn)
        confirm_btn.click()

        time.sleep(1)

        logger.info("register_rest_vaccine: confirm")

        for i in range(1, 100):
            response_url = "%s" % driver.current_url

            if response_url.find("progress") != -1:
                logger.info("register_rest_vaccine: progress to reserve: %s" % driver.current_url)
                time.sleep(1)
                continue
            elif response_url.find("failure") != -1:
                logger.info("register_rest_vaccine: fail to reserve: %s" % driver.current_url)
                break
            elif response_url.find("success") != -1:
                logger.info("register_rest_vaccine: success to reserve: %s" % driver.current_url)
                time.sleep(3)
                return True
            else:
                logger.info("register_rest_vaccine: unknown to reserve: %s" % driver.current_url)

        time.sleep(3)

        logger.info("register_rest_vaccine: %s" % json_item)

        return False

    except Exception as ex:
        logger.info("register_rest_vaccine 실패: %s " % ex)

    return False


# 백신을 가지고 있는 병원을 네이버잔여백신에서 접종예약신청
def check_hospital(hospital, driver):
    logger = logging.getLogger("check_hospital")
    try:
        # driver.switch_to.window(h_id)
        driver.switch_to.window("hospital")

        # key가 있는지 확인 없으면 param으로 접근후 key 획득
        if hospital.key == 0:
            driver.get("https://v-search.nid.naver.com/reservation?%s" % hospital.reservation_param)
            hospital.key = driver.find_element_by_id("key").get_attribute("value")
            logger.info("check_hospital: find key=%s" % hospital.key)
        else:
            driver.get("https://v-search.nid.naver.com/reservation/info?key=%s" % hospital.key)

        # 무조건 예약신청 버튼 누름
        # 예약신청
        # logger.info("check_hospital: find confirm button")
        confirm_btn = driver.find_element_by_id("reservation_confirm")

        confirm_class = confirm_btn.get_attribute("class")

        # logger.info("check_hospital: confirm class = %s" % confirm_class)

        if confirm_class != "link_confirm on":
            time.sleep(0.5)
            return False

        logger.info("check_hospital: confirm button is on, click confirm button")

        confirm_btn.click()

        logger.info("check_hospital: confirm")

        time.sleep(2)

        for n in range(1, 100):
            response_url = "%s" % driver.current_url

            if response_url.find("progress") != -1:
                logger.info("check_hospital: progress to reserve: %s" % driver.current_url)
                time.sleep(1)
                continue
            elif response_url.find("failure") != -1:
                logger.info("check_hospital: fail to reserve: %s" % driver.current_url)
                break
            elif response_url.find("success") != -1:
                logger.info("check_hospital: success to reserve: %s" % driver.current_url)
                return True
            else:
                logger.info("check_hospital: unknown to reserve: %s" % driver.current_url)

        return False

    except Exception as ex:
        logger.info("check_hospital 실패: %s at hospital_id=%s" % (ex, hospital.hospital_id))

    return False


# 현재 check할 hospital_id를 config에서 가져오기

def get_hospital():
    logger = logging.getLogger("get_hospital")
    try:
        current_time = strftime("%H:%M:%S", localtime())

        for hospital in config.h_list:
            if hospital.start_time < current_time < hospital.end_time:
                return hospital

    except Exception as ex:
        logger.info("get_hospital 실패: %s " % ex)

    return None


def check_naver_alarm2(driver):
    logger = logging.getLogger("check_naver_alarm")
    try:

        # 네이버 알림화면에서 새로운 알림 확인
        driver.get("https://talk.naver.com/ct/w4ocfa")

        ele = driver.find_element_by_id('__NEXT_DATA__')

        # logger.info(ele.get_attribute("innerHTML"))

        resp_json_data = json.loads(ele.get_attribute("innerHTML"))

        # logger.info(resp_json_data)

        message_list_json = resp_json_data.get("props").get('pageProps').get('userChatConfig').get('config').get(
            'messageList')

        item = message_list_json[len(message_list_json) - 1]

        # 시간 구하기
        alarm_time = item.get('date')
        register_url = item.get('customContent').get('linkList')[0].get('url')

        # logging.info(" config.last_alarm_time = %s, alarm_time = %s " % (config.last_alarm_time, alarm_time))

        if config.last_alarm_time == '':
            # 처음 시작으로 제외
            config.last_alarm_time = alarm_time
            return False
        elif alarm_time == config.last_alarm_time:
            # 새로운 알람 없음
            return False

        # 새로운 알람
        """ 클릭보다 바로 접근
        # 지금 신청하기 클릭
        btn_basic = item.find_element_by_class_name("btn_basic")
        btn_basic.click()
        """

        driver.get(register_url)

        # 예약신청
        # logger.info("register_rest_vaccine: find confirm button")
        confirm_btn = driver.find_element_by_id("reservation_confirm")

        # logger.info("register_rest_vaccine: click confirm button")
        # driver.execute_script("arguments[0].click();", confirm_btn)
        confirm_btn.click()

        time.sleep(1)

        logger.info("check_naver_alarm: confirm")

        for i in range(1, 100):
            response_url = "%s" % driver.current_url

            if response_url.find("progress") != -1:
                logger.info("check_naver_alarm: progress to reserve: %s" % driver.current_url)
                time.sleep(1)
                continue
            elif response_url.find("failure") != -1:
                logger.info("check_naver_alarm: fail to reserve: %s" % driver.current_url)
                break
            elif response_url.find("success") != -1:
                logger.info("check_naver_alarm: success to reserve: %s" % driver.current_url)
                time.sleep(3)
                return True
            else:
                logger.info("check_naver_alarm: unknown to reserve: %s" % driver.current_url)
                time.sleep(1)

        time.sleep(3)

        # 마지막 변경
        config.last_alarm_time = alarm_time

    except Exception as ex:
        logger.info("check_naver_alarm 실패: %s " % ex)

    return False


# 네이버 로그인
def login_naver_alarm():
    logger = logging.getLogger("login_naver")
    try:
        # alarm 브라우저 프로필 가져오기, 새 머신에서는 네이버 브라우저 등록, 인증서 등록할것

        if config.CONFIG['browser'] == 'chrome':

            #
            # naver에서 navigator.webdriver 채크함. 아래 옵션으로 navigator.webdriver 채크 피하기
            #

            options = webdriver.ChromeOptions()
            options.add_argument("user-data-dir=%s\\Chrome\\AlarmUser" % config.CONFIG['home_dir'])

            # options.add_argument("start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-blink-features=AutomationControlled")
            # browser 표시 여부, browser 띄우면 병원페이지 0.5초 예약페이지 0.5초 걸림
            # options.add_argument("--headless");

            # naver 로그인
            driver = webdriver.Chrome(options=options)

            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/83.0.4103.53 Safari/537.36'})
            logger.info(driver.execute_script("return navigator.userAgent;"))

        elif config.CONFIG['browser'] == 'firefox':
            fp = webdriver.FirefoxProfile('C:\\Users\\user\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles'
                                          '\\2cyrg3xs.default-release')
            driver = webdriver.Firefox(firefox_profile=fp)

        driver.get('https://nid.naver.com/nidlogin.login')

        # id, pw 입력할 곳을 찾습니다.
        tag_id = driver.find_element_by_name('id')
        tag_pw = driver.find_element_by_name('pw')
        tag_id.clear()
        time.sleep(1)

        # id 입력
        tag_id.click()
        tag_id.clear()
        pyperclip.copy(config.CONFIG['naver_id'])
        tag_id.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        # pw 입력
        tag_pw.click()
        tag_pw.clear()
        pyperclip.copy(config.CONFIG['naver_pw'])
        tag_pw.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        # 로그인 버튼을 클릭합니다
        login_btn = driver.find_element_by_id('log.login')
        login_btn.click()

        # 잔여백신으로 이동

        time.sleep(1)

        driver.get('https://talk.naver.com/ct/w4ocfa')

        time.sleep(1)

        return driver

    except Exception as ex:
        logger.info("login_naver 실패: %s " % ex)


def alarm_threading_main():
    # naver으로 login
    driver = login_naver_alarm()

    for i in range(1, 100000):
        check_naver_alarm2(driver)
        time.sleep(2)


# 전체 병원 정보 가져옴
def initialize_h_hashmap(driver):
    logger = logging.getLogger("initialize_h_hashmap")

    try:
        url = "https://api.place.naver.com/graphql"
        # logger.info("request :\n%s" % url)

        with open('%s\\data.json' % config.CONFIG['home_dir'], 'r', encoding="UTF-8") as f:
            json_data = f.readline().encode("utf-8")

        headers = {'Content-type': 'application/json',
                   'cookie': '%s' % driver.get_cookies(),
                   'origin': 'https://m.place.naver.com',
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'}

        # logger.info("send request :\n%s" % json_data)
        resp = requests.post(url, data=json_data, headers=headers)

        # logger.info("response status: %d" % resp.status_code);
        # logger.info("response body:\n%s" % resp.text);

        rest_json_data = json.loads(resp.text)

        json_array = rest_json_data[0].get("data").get('rests').get('businesses').get('items')

        # pprint.pprint(json_array)

        for item in json_array:

            vaccine_quantity = item.get('vaccineQuantity')

            if vaccine_quantity is None:
                continue

            sid = item.get('id')
            org_code = vaccine_quantity.get('vaccineOrganizationCode')

            try:
                driver.get("https://v-search.nid.naver.com/reservation?orgCd=%s&sid=%s" % (org_code, sid))
                key = driver.find_element_by_id("key").get_attribute("value")

                logger.info("initialize_h_hashmap: id=%s, key=%s" % (sid, key))

                config.h_hashmap[sid] = key

            except Exception as ex:

                name = item.get('name')
                logger.info("initialize_h_hashmap: fail to get key of id=%s, name=%s" % (sid, name))

            time.sleep(1)

        logger.info("initialize_h_hashmap: total %s " % len(config.h_hashmap))

    except Exception as ex:
        logger.info("initialize_h_hashmap 실패: %s " % ex)


# 스캐줄 있는 병원 정보만 가져옴, 전체는 못가져옴
def initialize_h_hashmap2(driver):
    logger = logging.getLogger("initialize_h_hashmap")

    try:

        for hospital in config.h_list:
            if hospital.hospital_id in config.h_hashmap:
                continue

            try:
                driver.get("https://v-search.nid.naver.com/reservation?%s" % hospital.reservation_param)
                key = driver.find_element_by_id("key").get_attribute("value")

                logger.info("initialize_h_hashmap: id=%s, name=%s, key=%s" % (hospital.hospital_id, hospital.name, key))

                config.h_hashmap[hospital.hospital_id] = key

            except Exception as ex:

                logger.info(
                    "initialize_h_hashmap: fail to get key of id=%s, name=%s" % (hospital.hospital_id, hospital.name))

            time.sleep(1)

        logger.info("initialize_h_hashmap: total %s " % len(config.h_hashmap))

    except Exception as ex:
        logger.info("initialize_h_hashmap 실패: %s " % ex)


def check_rest_vaccine(driver):
    logger = logging.getLogger("check_rest_vaccine")

    check_count = 0

    try:
        url = "https://api.place.naver.com/graphql"
        # logger.info("request :\n%s" % url)

        with open('%s\\data.json' % config.CONFIG['home_dir'], 'r', encoding="UTF-8") as f:
            json_data = f.readline().encode("utf-8")

        headers = {'Content-type': 'application/json',
                   'cookie': '%s' % driver.get_cookies(),
                   'origin': 'https://m.place.naver.com',
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'}

        # logger.info("send request :\n%s" % json_data)
        resp = requests.post(url, data=json_data, headers=headers)

        # logger.info("response status: %d" % resp.status_code);
        # logger.info("response body:\n%s" % resp.text);

        rest_json_data = json.loads(resp.text)

        json_array = rest_json_data[0].get("data").get('rests').get('businesses').get('items')

        # pprint.pprint(json_array)

        for item in json_array:

            check_count = check_count + 1

            vaccine_quantity = item.get('vaccineQuantity')

            if vaccine_quantity is None:
                continue

            total_quantity = vaccine_quantity.get('totalQuantity')

            if total_quantity == 0:
                continue

            sid = item.get('id')

            # 화이자
            is_pfizer = False
            for vaccine_item in vaccine_quantity.get("list"):
                quantity = vaccine_item.get("quantity")
                vaccine_type = vaccine_item.get("vaccineType")

                if quantity > 0 and vaccine_type == '화이자':
                    is_pfizer = True
                    logger.info("vaccine type : %s" % vaccine_type)
                    break

            # 백신이 1개이상이면 바로 예약
            if total_quantity > 0 and sid in config.h_hashmap and is_pfizer:  # and vaccine_type == "화이자":
                # key으로 직접 예약

                key = config.h_hashmap[sid]
                cd = 'VEN00013'
                reservation_url = "https://v-search.nid.naver.com/reservation/progress?key=%s&cd=%s" % (key, cd)

                # 메인 화면으로 이동
                driver.switch_to.window(my_driver.window_handles[0])
                driver.get(reservation_url)

                logger.info("vaccine available : \n %s" % item)

                for i in range(1, 100):
                    response_url = "%s" % driver.current_url

                    if response_url.find("progress") != -1:
                        logger.info("check_rest_vaccine: progress to reserve: %s" % driver.current_url)
                        time.sleep(1)
                        continue
                    elif response_url.find("failure") != -1:
                        logger.info("check_rest_vaccine: fail to reserve: %s" % driver.current_url)
                        break
                    elif response_url.find("success") != -1:
                        logger.info("check_rest_vaccine: success to reserve: %s" % driver.current_url)
                        time.sleep(3)
                        return True, check_count
                    else:
                        logger.info("check_rest_vaccine: unknown to reserve: %s" % driver.current_url)
                        time.sleep(1)

            elif total_quantity > 0 and sid not in config.h_hashmap and is_pfizer:
                # 기존방식으로 등록
                driver.switch_to.window(my_driver.window_handles[0])
                return register_rest_vaccine(item, driver), check_count

    except Exception as ex:
        logger.info("check_rest_vaccine 실패: %s " % ex)

    return False, check_count


#
# main
#
logger = logging.getLogger("main")
logging.info('start sylvan')

# naver으로 login
my_driver = login_naver()

# 직접 예약등록하는 key 확인
initialize_h_hashmap2(my_driver)

# naver_alarm 채크용 threading
# t = threading.Thread(target=alarm_threading_main)
# t.start()

# open tab windows with hospital_id
my_driver.execute_script("window.open('about:blank','hospital');")

last_hospital_id = 0

# 확인 루프
for count in range(1, 100000):

    #
    # 개별 병원 확인
    # 시간당 1000번 조회 넘으면 블럭당함, 현재 4초에 한번 분당 15개 정도 조회
    #
    hospital = get_hospital()
    if hospital is not None:
        my_driver.switch_to.window('hospital')

        # 이전 페이지와 틀리면 page get
        if last_hospital_id != hospital.hospital_id:
            logger.info("check %s between %s and %s" % (hospital.name, hospital.start_time, hospital.end_time))
            last_hospital_id = hospital.hospital_id

        if check_hospital(hospital, my_driver):
            break
    else:
        time.sleep(1)
        # my_driver.switch_to.window(my_driver.window_handles[0])

    #
    # 전체 맵 확인
    #

    result, check_count = check_rest_vaccine(my_driver)

    if result is True:
        logger.info("%s check %s hospitals: success to reservce vaccine ")
        break

    """
    # restful api으로 잔여백신 정보 가져오기
    json_data = get_rest_vaccine_info2(my_driver)

    # 잔여백신있는 병원 찾기
    json_item, check_count = find_rest_vaccine(json_data)

    if check_count > 0 and json_item != "None" and len(json_item) > 0:
        # 잔여백신예약신청 하고 중지

        # 메인 화면으로 이동
        my_driver.switch_to.window(my_driver.window_handles[0])

        if register_rest_vaccine(json_item, my_driver):
            break
    """

    count = count + 1

    logger.info("%s check %s hospitals: no vaccine available " % (count, check_count))

    # 가끔식 화면 refresh
    if count % 30 == 0:
        my_driver.switch_to.window(my_driver.window_handles[0])

        my_driver.get('https://m.place.naver.com/rest/vaccine?vaccineFilter=used'
                      '&x=%s&y=%s&bounds=%s' % (config.CONFIG['x'], config.CONFIG['y'], config.CONFIG['bounds']))

    # 매크로방지 피하기 위해서 1초~3초 랜덤하게 쉬기
    time.sleep(random.randrange(1, 3))
