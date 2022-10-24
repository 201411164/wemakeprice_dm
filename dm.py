import sqlite3
from telnetlib import EC
import json
import urllib.request
import re
import selenium

from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from random import randrange
from method import *
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

now = datetime.now()


def insert_customer(customer_id, username, keyword, created_date=now.strftime('%Y-%m-%d %H:%M:%S'), is_sent='N'):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('쿼리 실행')

        cur.execute("insert into customer_account values (?, ?, ?, ?, ?)",
                    (customer_id, username, keyword, created_date, is_sent))

        cur.execute("SELECT * FROM customer_account")
        print('성공적으로 DB에 계정 추가 완료 : '+username)
        cur.close()
    except Exception as e:
        print(e)
        cur.close()


def update_customer(customer_id):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('비즈니스 계정의 발송여부를 변경합니다.')
        cur.execute(f"UPDATE customer_account SET is_sent = 'Y' WHERE customer_id = '{customer_id}' ")

        print(str(customer_id)+'계정의 여부 변경 완료.')

        cur.close()
        return 0

    except Exception as e:
        print(e)
        cur.close()


def insert_login(login_username, login_password, is_safe='Y', last_login_date='', created_date=now.strftime('%Y-%m-%d %H:%M:%S'), daily_sentcnt=0, is_banned='N', ban_reason=''):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('쿼리 실행')

        print(login_username)
        print(login_password)

        cur.execute("insert into login_account values (?, ?, ?, ?, ?, ?, ?, ?)",
                    (login_username, login_password, is_safe, last_login_date, created_date, daily_sentcnt, is_banned, ban_reason))

        cur.execute("SELECT * FROM login_account")
        print('성공적으로 DB에 로그인 계정 추가 완료 : '+login_username)
        cur.close()
    except Exception as e:
        print(e)
        print('계정이 이미 존재합니다.'+login_username)
        cur.close()


def delete_login(login_username):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('로그인 계정 삭제하기')
        print(login_username)
        cur.execute(f"SELECT login_password FROM login_account where login_username like '{login_username}'")
        row = cur.fetchone()
        login_password = row[0]
        print(login_password)

        cur.execute(f"DELETE FROM login_account where login_username like '{login_username}'")
        print('성공적으로 DB에서 로그인 계정 삭제 완료 : ' + login_username)

        #엑셀도 수정해주기

        df = pd.read_excel("account.xlsx")
        df = df.replace(np.nan, '', regex=True)
        account_id_list = []
        account_pw_list = []
        num = 0
        for userid, userpw in zip(df['ID'], df['PW']):
            account_id_list.append(df['ID'][num])
            account_pw_list.append(df['PW'][num])
            num = num + 1

        for i in account_id_list:
            print(i)
        for k in account_pw_list:
            print(k)

        print(login_username)
        account_id_list.remove(login_username)
        print(login_password)
        account_pw_list.remove(login_password)

        df_save = pd.DataFrame({
                'ID': account_id_list,
                'PW': account_pw_list
        })
        df_save.to_excel("account.xlsx")

        print('account.xlsx 파일에도 계정 삭제 반영 완료'+login_username)

        cur.close()

    except Exception as e:
        print(e)
        cur.close()


def insert_send(login_username, customer_username, created_date=now.strftime('%Y-%m-%d %H:%M:%S'), send_msg=''):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('insert send 쿼리 실행')

        customer_id = customer_username

        cur.execute("SELECT IFNULL(MAX(send_id), 0) FROM send_data")
        maxNum = cur.fetchone()[0]

        cur.execute("insert into send_data values (?, ?, ?, ?, ?)",
                    (int(maxNum)+1, login_username, customer_id, created_date, send_msg))

        cur.execute("SELECT * FROM send_data")

        print('성공적으로 DB에 발송 이력 추가 완료 : ' + login_username + str(customer_id))

        cur.close()
        print('고객 데이터 발송여부 업데이트')
        update_customer(customer_id)
    except Exception as e:
        print(e)
        cur.close()


def safe_login_list():
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('Safe 계정 List 찾기')
        # 위메프는 인스타와 달리 발송 개수 제한 20개 없앰
        cur.execute("SELECT login_username, login_password, daily_sentcnt FROM login_account where is_banned = 'N'")


        row = cur.fetchall()
        cur.close()
        return row

    except Exception as e:
        print(e)
        cur.close()
        return []


def customer_list():
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('Customer 계정 List 찾기')

        cur.execute("SELECT customer_id, username, keyword FROM customer_account where is_sent = 'N'")
        row = cur.fetchall()
        cur.close()
        return row

    except Exception as e:
        print(e)
        cur.close()
        return []

def login_get_one_account():
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('위메프는 인스타와 달리 밴 관리 X, 로그인 계정 1개 정보 가져오는 중')

        cur.execute(
            "SELECT IFNULL(MAX(login_username), ''), login_password, daily_sentcnt FROM login_account limit 1")
        row = cur.fetchone()
        cur.close()
        if row[0] != '':
            return row
        else:
            print('로그인 가능한 계정이 없습니다.')
            return False

    except Exception as e:
        print(e)
        cur.close()
        return []


# def login_cnt_update():
#     try:
#         conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
#         cur = conn.cursor()
#
#         print('마지막 로그인 후 하루 이상 지난 계정들을 초기화합니다')
#
#         cur.execute("SELECT COUNT(*) FROM login_account where DATETIME(last_login_date, '+1 day') < CURRENT_TIMESTAMP")
#         row = cur.fetchone()[0]
#         print(str(row)+'개의 계정들이 마지막 로그인 후 하루 이상 경과, 초기화 가능합니다.')
#
#         cur.execute(f"UPDATE login_account SET daily_sentcnt = 0 WHERE DATETIME(last_login_date, '+1 day') < CURRENT_TIMESTAMP")
#
#         print(cur.fetchall())
#         print('총'+str(row)+'개의 계정들을 Safe 계정으로 변경 완료')
#         cur.execute("SELECT COUNT(*) FROM login_account where daily_sentcnt < 20 AND is_banned = 'N'")
#         cnt = int(cur.fetchone()[0])
#         print('사용 가능한 계정 수 :' + str(cnt) + '개 확인됨.')
#         cur.close()
#         return cnt
#
#     except Exception as e:
#         print(e)
#         cur.close()


def login_banned_update(login_username, ban_reason=''):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        cur.execute(f"UPDATE login_account SET is_banned = 'Y' WHERE login_username = '{login_username}'")
        cur.execute(f"UPDATE login_account SET ban_reason = '{ban_reason}' WHERE login_username = '{login_username}'")

        cur.close()

    except Exception as e:
        print(e)
        cur.close()


def login_unbanned_update(login_username):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('로그인 성공한 계정을 분류해 banned ID에서 해제합니다'+login_username)

        cur.execute(f"UPDATE login_account SET is_banned = 'N' WHERE login_username = '{login_username}'")
        cur.execute(f"UPDATE login_account SET ban_reason = '' WHERE login_username = '{login_username}'")

        print('unbanned id update 완료')

        cur.close()

    except Exception as e:
        print(e)
        print('banned id update 실패')
        cur.close()


def login_date_update(login_username):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('로그인한 계정의 마지막 로그인 일시를 업데이트합니다')

        cur.execute(f"UPDATE login_account SET last_login_date = CURRENT_TIMESTAMP WHERE login_username = '{login_username}'")

        cur.close()

    except Exception as e:
        print(e)
        cur.close()


def login_cnt_increase(username):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        print('현재 로그인한 계정의 발송 카운트를 증가시킵니다.')

        cur.execute(f"SELECT daily_sentcnt FROM login_account where login_username = '{username}' ")
        curCount = int(cur.fetchone()[0])

        print(username + '계정 : ' + str(curCount) + '---- 현재 발송개수')

        cur.execute(f"UPDATE login_account SET daily_sentcnt = daily_sentcnt+1 WHERE login_username = '{username}' ")
        print(username+'계정의 발송 카운트를 증가 완료.')
        curCount = curCount + 1
        print(username + '계정 : ' + str(curCount) + '---- 현재 발송개수')
        cur.close()
        return curCount


    except Exception as e:
        print(e)
        cur.close()


def customer_check(username):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        # print('이미 DB에 있는 고객계정인지 확인, 있으면 True, 없으면 False')

        cur.execute(f"SELECT IFNULL(MAX(username), '') FROM customer_account where username = '{username}' ")
        curCount = (cur.fetchone()[0])

        if curCount == '':
            cur.close()
            return False
        else:
            cur.close()
            return True

    except Exception as e:
        print(e)
        cur.close()


def customer_send_check(username):
    try:
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()

        # print('이미 발송한 고객인지 확인, 있으면 True, 없으면 False')

        # cur.execute(f"SELECT IFNULL(MAX(username), '') FROM customer_account where username = '{username}' and is_sent = 'Y'")
        cur.execute("SELECT IFNULL(MAX(username), '') FROM customer_account where username = " + '"' + username + '"' + " and is_sent = 'Y'")
        curCount = (cur.fetchone()[0])

        if curCount == '':
            cur.close()
            return False
        else:
            cur.close()
            return True

    except Exception as e:
        print(e)
        cur.close()




def login(user_id, user_pw, driver):
    print('login 시작....')
    login_banned_update(user_id, '')
    try:
        # 로그인
        pyperclip.copy(user_id)
        driver.find_element(By.ID, '_loginId').send_keys(Keys.CONTROL + 'v')  # 아이디 복붙
        time.sleep(2)
        pyperclip.copy(user_pw)
        driver.find_element(By.ID, '_loginPw').send_keys(Keys.CONTROL + 'v')  # pw 복붙
        time.sleep(3)  # 3초 쉬기
        driver.find_element(By.ID, "_userLogin").click()
        # driver.find_element(By.CLASS_NAME, 'sqdOP.L3NKy.y3zKF').click()  # 로그인 버튼
        random_sleep = random.randrange(5, 8)
        time.sleep(random_sleep)
        return True

    except Exception as h:
        login_banned_update(user_id, '계정정보 오류 등으로 로그인 자체가 불가능함')
        print(h)
        print("Login Exception")
        return False


def logout(driver):
    try:
        print('로그아웃을 시도합니다... 좌측 네비게이션 바인지 확인중...')
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//div[text()='프로필']"))
        )
        # 좌측 사이드바
        driver.find_element(By.XPATH, "//div[text()='프로필']").click()  # 프로필 클릭
        time.sleep(2)
        driver.find_elements(By.CLASS_NAME, "_abm0")[-1].click()  # 톱니바퀴 클릭
        time.sleep(2.5)
        driver.find_element(By.XPATH, "//button[text()='로그아웃']").click()  # 로그아웃 클릭
    except:
        # 상단 사이드바인 경우인지 확인
        print('로그아웃을 시도합니다... 상단 네비게이션 바인지 확인중...')
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "_6q-tv"))
            )
            driver.find_elements(By.CLASS_NAME, "_6q-tv")[-1].click()  # 프로필 클릭
            time.sleep(1.5)
            driver.find_element(By.XPATH, "//div[text()='로그아웃']").click()  # 로그아웃 클릭
        except:
            # 상단 사이드바인 경우인지 확인 - PC 환경에 따라 클래스명이 바뀜
            print('로그아웃을 시도합니다... 상단 네비게이션 바 확인중...')
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "_aa8j"))
                )
                driver.find_elements(By.CLASS_NAME, "_aa8j")[-1].click()  # 프로필 클릭
                time.sleep(1.5)
                driver.find_element(By.XPATH, "//div[text()='로그아웃']").click()  # 로그아웃 클릭
            except:
                try:
                    print('로그아웃을 시도합니다... 계정에 문제가 있는 경우인지 확인합니다...')
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, """//div[text()='다른 계정으로 로그인']"""))
                    )
                    driver.find_element(By.XPATH, """//div[text()='다른 계정으로 로그인']""").click()
                    time.sleep(1.5)
                    driver.find_element(By.XPATH, "//button[text()='로그아웃']").click()  # 로그아웃 클릭
                except Exception as e:
                    try:
                        driver.find_element(By.XPATH, """//a[text()='로그아웃']""").click()
                        time.sleep(2)
                        print('의심스러운 계정 활동 에러 발생')
                    except:
                        print('기존에 발생하지 않았던 에러 발생')
                        clear_cache(driver)
                        time.sleep(4)
                        return

def dm_send(login_username, d, k, message, driver, model):
    curCount = 0
    try:

        #URL이 텍스트에 포함되어있으면 REGEX를 이용해서 추출하기
        if message.find('http') >= 0:
            urlLink = re.findall(r'(https?://\S+)', message)[0] #한 텍스트에 링크가 여러 개 들어 있더라도 링크는 하나만 추출하기
            newMessage = message.replace(urlLink, "")

        # 랜덤하게 DM 메시지 골라서 전송
        # DM 줄바꿈 지원 추가, 개행일때마다 Shift Enter 입력하도록 -20220921 고동욱
        for part in newMessage.split('\n'):
            driver.find_element(By.CSS_SELECTOR, "textarea").send_keys(part)
            ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(
                Keys.ENTER).perform()

        driver.find_element(By.CSS_SELECTOR, "textarea").send_keys(Keys.ENTER)

        # 마지막으로 링크 보내기
        pyperclip.copy(urlLink)
        driver.find_element(By.CSS_SELECTOR, "textarea").send_keys(Keys.CONTROL + 'v')
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "textarea").send_keys(Keys.ENTER)

        # 발송 기록 남기기
        insert_send(login_username, d, now.strftime('%Y-%m-%d %H:%M:%S'), message) #발송 기록에는 링크도 포함시키기
        curCount = login_cnt_increase(login_username)
        random_sleep = random.randrange(5, 10)
        time.sleep(random_sleep)
        # 발송 수 증가시키기
        return curCount

    except Exception as e:
        print(e)
        return 0

    # ####### 발송후 리스트에서 삭제하고 엑셀로 저장 ###############
    #
    # account_final_list_save.remove(d)
    # matching_final_keyword_lis_save.remove(k)
    # df_save_log = pd.DataFrame({
    #     '계정': account_final_list_save,
    #     '키워드': matching_final_keyword_lis_save
    # })
    # df_save_log.to_excel("남은계정.xlsx", index=True)


def perform_actions(driver, keys):
    actions = ActionChains(driver)
    actions.send_keys(keys)
    time.sleep(2)
    print('인터넷 캐시 삭제 완료!')
    actions.perform()


def clear_cache(driver, timeout=60):
    """Clear the cookies and cache for the ChromeDriver instance."""
    # navigate to the settings page
    try:
        driver.get('chrome://settings/clearBrowserData')
        perform_actions(driver, Keys.TAB * 2 + Keys.DOWN * 4 + Keys.TAB * 5 + Keys.ENTER)  # Tab to the time select and key down to say "All Time" then go to the Confirm button and press Enter
        time.sleep(6)
        driver.close()

    except Exception as e:
        print(e)
        driver.close()
    # # wait for the button to appear
    # wait = WebDriverWait(driver, timeout)
    # wait.until(get_clear_browsing_button)
    #
    # # click the button to clear the cache
    # get_clear_browsing_button(driver).click()

    # wait for the button to be gone before returning
    # wait.until_not(get_clear_browsing_button)



def dm_start(model):
    print("DM발송 자동화 시작")
    model.textBrowser.append("DM발송 자동화 시작")
    # limit = int(model.lineEdit_4.text())
    keywords = model.lineEdit.text()
    # content = model.textEdit.toPlainText()
    contentList = []
    if model.textEdit.toPlainText() != '':
        contentList.append(model.textEdit.toPlainText())
    if model.textEdit_2.toPlainText() != '':
        contentList.append(model.textEdit_2.toPlainText())
    if model.textEdit_3.toPlainText() != '':
        contentList.append(model.textEdit_3.toPlainText())
    if model.textEdit_4.toPlainText() != '':
        contentList.append(model.textEdit_4.toPlainText())
    print(str(len(contentList))+'개의 DM 메시지 확인. 랜덤으로 보냅니다.')

    customerList = customer_list()
    customerNum = len(customerList)

    if keywords != '': #키워드가 비어있고 DB에 데이터가 존재하는 경우 수집하지 않고 발송 시작

        driver = starter()
        driver.delete_all_cookies()
        clear_cache(driver)

        time.sleep(3)

        while True:
            try:
                #로그인 진행
                driver = starter()
                driver.get("https://front.wemakeprice.com/user/login?returnUrl=https%3A%2F%2Ffront.wemakeprice.com%2Fmain&type=GENERAL&orderYN=N&selectionYN=N")
                time.sleep(4)
                login_account = login_get_one_account()

                if not login_get_one_account():
                    print('로그인 가능한 계정이 없습니다.')
                    return

                isLogin = login(login_account[0], login_account[1], driver)

                if isLogin:
                    print("로그인 완료")
                    model.textBrowser.append("로그인 완료")
                    time.sleep(2)
                else:
                    print('로그인 재시도')
                    login_account = login_get_one_account()
                    login(login_account[0], login_account[1], driver)

                keyword_list = keywords.split(",")
                account_list = []
                element_box = []
                matching_keyword_list = []
                for keyword in keyword_list:
                    print('계정수집 시작')

                    pageNum = 0
                    for i in range(1, 100):
                        pageNum = pageNum + 1
                        url = f'https://search.wemakeprice.com/search?searchType=DEFAULT&_service=2&_type=3&search_cate=top&keyword={keyword}&_no=6&page={str(pageNum)}'
                        print(url)
                        driver.get(url)

                        time.sleep(5)

                        thumList = driver.find_elements(By.CLASS_NAME, "list_thum")
                        productNumList = []
                        urlList = []

                        try:
                            elemList = driver.find_elements(By.CSS_SELECTOR, "[data-gtm-action='검색결과리스트_클릭']")
                            num = 0
                            for k in elemList:
                                try:
                                    num = num + 1
                                    tempCustomerNum = k.get_attribute("data-gtm-link-value")
                                    tempUrl = re.findall(r'(https?://\S+)', k.get_attribute("href"))[0]
                                    print('확인한 상품 링크 :'+tempUrl)
                                    if 'wemakeprice.com' in tempUrl:
                                        productNumList.append(tempCustomerNum)
                                        urlList.append(tempUrl)
                                        print('위메프 상품, 링크 임시 저장')
                                    else:
                                        print('위메프 상품이 아닌 타사 쇼핑몰 링크, 톡톡 불가라 추가 안 함.')
                                except Exception as e:
                                    print(e)
                                    print(k.get_attribute("href"))
                                    continue
                            print(str(num)+'개의 링크 중' + str(len(urlList)) + '개의 위메프 상품 링크 수집 완료')
                            model.textBrowser.append(str(num)+'개의 링크 중' + str(len(urlList)) + '개의 위메프 상품 링크 수집 완료')

                        except Exception as e:
                            print(e)
                            time.sleep(3)
                            continue


                        for k in range(0, len(urlList)):

                            print('현재 페이지 ' + str(len(urlList))+'개의 링크 중 '+str(k)+'번째 링크 접속 시도 합니다.')

                            try:
                                url = urlList[k]
                                print(url)
                                driver.get(url)
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                thumList[k].click()
                                time.sleep(2)
                                continue

                            window_before = driver.window_handles[0]

                            time.sleep(5)

                            try:
                                #상품문의 클릭
                                driver.find_element(By.CLASS_NAME, "tit.prdt_qna_s").click()
                                time.sleep(3)

                                #톡상담버튼클릭
                                driver.find_element(By.CLASS_NAME, "btn_sys.sml_b.btn_talk").click()
                                print('톡 버튼 클릭 성공')
                                window_after = driver.window_handles[1]
                                driver.switch_to.window(window_after)
                                time.sleep(3)

                            except Exception as e:
                                print(e)
                                print('팝업창 등의 이유로 톡 버튼 클릭 불가, 다음 상품으로 넘어갑니다.')
                                continue

                            dm_message = contentList[random.randint(0, len(contentList) - 1)]

                            print('dm 보내기 실행')

                            try:
                                isSending = driver.find_element(By.CSS_SELECTOR, "textarea")
                                # TextArea 요소 유무로 문의상품 선택 창이 떴는지 판단하기. 문의상품을 골라야 할 경우 첫번째 품목 클릭하도록
                            except Exception as e:
                                try:
                                    driver.find_elements(By.CLASS_NAME, "image")[0].click()
                                    time.sleep(1)
                                    driver.find_elements(By.CLASS_NAME, "btn")[0].click()
                                    time.sleep(3)
                                except:
                                    print('상품 문의 창 오류, 다음 상품으로 넘어갑니다.')
                                    driver.close()
                                    driver.switch_to.window(window_before)
                                    continue



                            try:
                                companyName = driver.find_element(By.CLASS_NAME, "h1").text

                                if customer_send_check(companyName):
                                    print('보낸적 있는 계정입니다.'+companyName)
                                    driver.close()
                                    driver.switch_to.window(window_before)
                                    time.sleep(2)
                                else:
                                    try:
                                        insert_customer(productNumList[k], companyName, keyword,
                                                        now.strftime('%Y-%m-%d %H:%M:%S'), 'N')
                                        time.sleep(3)
                                        dm_send(login_account[0], productNumList[k], keyword, dm_message, driver, model)
                                        print('메시지 보내기 완료')
                                        # 팝업창 닫기
                                    except Exception as e:
                                        print(e)
                                    finally:
                                        driver.close()
                                        driver.switch_to.window(window_before)
                                        time.sleep(2)

                            except Exception as e:
                                print(e)
                                continue

            except:
                login_banned_update(login_account[0], '계정 수집 중 오류 발생')
                driver.delete_all_cookies()
                clear_cache(driver)
                time.sleep(4)
                print('다음 계정으로 넘어가 계정을 수집합니다')

    elif customerNum > 0:
        print('키워드를 입력하지 않았고 DB에 저장되어 있는 미발송 고객 계정들이 있습니다. 해당 계정들에게 메시지를 보냅니다.')
    else:
        print('키워드를 입력하지 않았지만 DB에 저장되어 있는 미발송 고객 계정이 없습니다. 키워드를 입력해주세요')
        return

    ###########  계정 수집 종료 ####################


    print(f"프로그램 종료")



        # driver.find_element(By.CLASS_NAME, "_aa8j").click()
        # time.sleep(1)
        # driver.find_element(By.XPATH, "//div[text()='로그아웃']").click()
        # time.sleep(3)
        # driver.close()


