import sqlite3

import dm
from method import *


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def launch_db():
    conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
    cur = conn.cursor()

    # cur.execute("SELECT * FROM send_data")
    #
    # # rows = cur.fetchall()
    cur.execute(
        "CREATE TABLE if not exists login_account(login_username str PRIMARY KEY, login_password TEXT, is_safe TEXT, last_login_date TEXT, created_date TEXT, daily_sentcnt INT, is_banned TEXT, ban_reason TEXT)")

    print('기존 계정에 더해 account.xlsx 파일에서 계정 정보를 추가합니다.')
    df = pd.read_excel("account.xlsx")
    df = df.replace(np.nan, '', regex=True)

    num = 0
    for userid, userpw in zip(df['ID'], df['PW']):
        dm.insert_login(df['ID'][num], df['PW'][num])
        num = num + 1

    cur.execute(
        "CREATE TABLE if not exists customer_account(customer_id int PRIMARY KEY, username TEXT, keyword TEXT, created_date TEXT, is_sent TEXT)")

    cur.execute(
        "CREATE TABLE if not exists send_data(send_id integer PRIMARY KEY AUTOINCREMENT, login_username TEXT, customer_id TEXT, created_date TEXT, send_msg TEXT, CONSTRAINT customer_id FOREIGN KEY(customer_id) references customer_account(customer_id))")

    # cur.execute(
    #     "INSERT INTO send_data VALUES (1234, 'testid', 'myid', 'testkeyword', '2020-04-01 00:00:00.000')")

    cur.close()


def password_check():
    driver = starter_headless()
    #블로그에 비밀번호를 적어두어 변경 가능하도록
    driver.get("https://blog.naver.com/PostList.naver?blogId=sandlfscxyvn072&widgetTypeCall=true&directAccess=true")
    time.sleep(1.5)
    realPassword = driver.find_element(By.ID, 'SE-4288f314-8ae9-40d0-bf9c-ad06294518f7').text

    userPassword = input("비밀번호를 입력하세요: ")
    while True:
        if userPassword in [realPassword]:
            print('올바른 비밀번호 입니다. 통과')
            break
        else:
            print("잘못된 비밀번호 입니다. 비밀번호 문의 : 010-3563-8987")
            time.sleep(3)
            userPassword = input("비밀번호를 입력하세요: ")


password_check()
launch_db()
# dm.login_cnt_update() 위메프에서는 사용안함
form = resource_path('instagram_dm.ui')
form_class = uic.loadUiType(form)[0]


class MyWindow(QtWidgets.QMainWindow, QMessageBox, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.start_btn)
        self.pushButton_2.clicked.connect(self.refresh_btn)
        # self.pushButton_2.clicked.connect(self.continue_btn)

        try:

            self.load_data()

            # 메뉴바 활성화
            self.tableWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            # 우클릭시 메뉴바 생성
            self.tableWidget.customContextMenuRequested.connect(self.generate_menu)
        except Exception as e:
            print(e)
            print('DB 확인되지 않음, DB 생성 진행합니다.')


    def generate_menu(self, pos):
        # 빈공간에서
        if (self.tableWidget.itemAt(pos) is None):
            self.emptymMenu = QMenu(self)
            self.emptymMenu.addAction("추가", self.addRow)
            self.emptymMenu.exec_(self.tableWidget.mapToGlobal(pos))

            # 아이템에서
        else:
            self.menu = QMenu(self)
            self.menu.addAction("삭제", lambda: self.delete_login_row(pos))
            self.menu.addAction("밴 해제하기", lambda: self.unban_login_row(pos))
            self.menu.addAction("계정 밴하기", lambda: self.ban_login_row(pos))
            self.menu.exec_(self.tableWidget.mapToGlobal(pos))

    def addRow(self):
        print("추가")
        # 마지막줄에 추가하기 위함
        rowPosition = self.tableWidget.rowCount()
        columnPosition = self.tableWidget.columnCount()
        self.tableWidget.insertRow(rowPosition)

        # 모든 열에 세팅
        for column in range(columnPosition):
            self.tableWidget.setItem(rowPosition, column, QTableWidgetItem(''))

    def delete_login_row(self, pos):
        try:
            curIndex = self.tableWidget.indexAt(pos).row()    #현재 Row Num 가져오기
            loginId = self.tableWidget.item(curIndex, 0).text() #Row, Column에 해당하는 아이템을 가져옴, 이 경우에는 ID
            dm.delete_login(loginId)
            self.tableWidget.removeRow(self.tableWidget.indexAt(pos).row())
            self.load_data()
            print("삭제 성공", pos)
        except Exception as e:
            print(e)
            print("삭제 실패", pos)

    def unban_login_row(self, pos):
        try:
            curIndex = self.tableWidget.indexAt(pos).row()  #현재 Row Num 가져오기
            loginId = self.tableWidget.item(curIndex, 0).text()  #Row, Column에 해당하는 아이템을 가져옴, 이 경우에는 ID

            dm.login_unbanned_update(loginId)
            self.load_data()
            print("밴 해제 성공", pos)
        except Exception as e:
            print(e)
            print("밴 해제 실패", pos)

    def ban_login_row(self, pos):
        try:
            curIndex = self.tableWidget.indexAt(pos).row()  #현재 Row Num 가져오기
            loginId = self.tableWidget.item(curIndex, 0).text()  #Row, Column에 해당하는 아이템을 가져옴, 이 경우에는 ID
            dm.login_banned_update(loginId, '')
            self.load_data()
            print("계정 밴 성공", pos)
        except Exception as e:
            print(e)
            print("계정 밴 실패", pos)



    def load_data(self):
        conn = sqlite3.connect("wemakeprice.db", isolation_level=None)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM login_account")
        actNum = int(cur.fetchone()[0])
        sql = 'SELECT * FROM login_account'
        cur.execute(sql)
        results = cur.fetchall()

        tablerow = 0

        self.tableWidget.setRowCount(actNum)
        self.tableWidget.setColumnCount(8)
        column_idx_lookup = {'login_username': 0, 'login_password': 1, 'is_safe': 2, 'last_login_date': 3,
                             'created_date': 4, 'daily_sentcnt': 5, 'is_banned': 6, 'ban_reason': 7}
        column_headers = ['로그인 ID', '로그인 비밀번호', '세이프계정여부', '마지막 로그인 날짜', '생성일', '누적 발송건수', '밴 여부', '밴 사유']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        col = -1
        row = -1
        for k in results:
            col = col + 1
            row = -1
            for v in k:
                row = row + 1
                self.tableWidget.setItem(col, row, QTableWidgetItem(str(v)))

        cur.execute("SELECT COUNT(*) FROM customer_account")
        actNum2 = int(cur.fetchone()[0])
        sql = 'SELECT * FROM customer_account order by 4 desc'
        cur.execute(sql)
        results2 = cur.fetchall()

        self.tableWidget2.setRowCount(actNum2)
        self.tableWidget2.setColumnCount(5)
        column_headers = ['고객 계정 고유번호', '고객 계정 ID', '키워드', '생성일', 'DM발송여부']
        self.tableWidget2.setHorizontalHeaderLabels(column_headers)
        self.tableWidget2.setEditTriggers(QAbstractItemView.NoEditTriggers)

        col = -1
        row = -1
        for k in results2:
            col = col + 1
            row = -1
            for v in k:
                row = row + 1
                self.tableWidget2.setItem(col, row, QTableWidgetItem(str(v)))

        cur.execute("SELECT COUNT(*) FROM send_data")
        actNum3 = int(cur.fetchone()[0])
        sql = 'SELECT * FROM send_data order by 1 desc'
        cur.execute(sql)
        results3 = cur.fetchall()

        self.tableWidget3.setRowCount(actNum3)
        self.tableWidget3.setColumnCount(5)
        column_headers = ['발송이력 관리번호', '로그인 ID', '고객 계정 고유번호', '전송일', '보낸 메시지']
        self.tableWidget3.setHorizontalHeaderLabels(column_headers)
        self.tableWidget3.setHorizontalHeaderLabels(column_headers)

        col = -1
        row = -1
        for k in results3:
            col = col + 1
            row = -1
            for v in k:
                row = row + 1
                self.tableWidget3.setItem(col, row, QTableWidgetItem(str(v)))

        cur.close()

    def start_btn(self):
        qqq = threading.Thread(target=dm.dm_start, args=(model,))
        qqq.start()
        self.pushButton.setDisabled(True)
        time.sleep(5)
        self.pushButton.setEnabled(True)

    def refresh_btn(self):
        self.load_data()

    # def continue_btn(self):
    #     qqq = threading.Thread(target=continue_dm.continue_dm_start, args=(model,))
    #     qqq.start()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = MyWindow()
    model.show()
    app.exec_()
    sys.exit(app.exec_())
