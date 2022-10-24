from moduls import *

chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
chromedriver_autoinstaller.install(True)
s = f'./{chrome_ver}/chromedriver.exe'

### 셀레니움 스타터 세팅
def starter():
    user_agent = "Mozilla/5.0 (Linux; Android 9; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.83 Mobile Safari/537.36"

    option = Options()
    subprocess.Popen(
        r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')  # 디버거 크롬 구동
    option.add_argument('user-agent=' + user_agent)
    option.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    option.add_argument('window-size=1920x1080')
    option.add_argument('lang=ko_KR')
    option.add_argument(f'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36')
    option.add_argument('start-maximized')

    driver = webdriver.Chrome(executable_path=s, options=option)
    driver.implicitly_wait(20)

    return driver


def starter_headless():
    user_agent = "Mozilla/5.0 (Linux; Android 9; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.83 Mobile Safari/537.36"

    option = Options()
    option.add_argument('window-size=1920x1080')
    option.add_argument('--headless')
    option.add_argument('lang=ko_KR')
    option.add_argument(f'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36')
    option.add_argument('start-maximized')

    driver = webdriver.Chrome(executable_path=s, options=option)
    driver.implicitly_wait(20)


    return driver



### 리스트를 원하는 개수로 나눠서 리스트화 하기
def list_chunk(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


## 파일개수 확인하는 함수
def get_files_count(folder_path):
    dirListing = os.listdir(folder_path)
    return len(dirListing)


##
def time_check():
    tms = time.localtime()
    result_time = time.strftime('%Y.%m.%d %I:%M:%S %p', tms)
    return result_time


def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print(downloaded, total, status)

