import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QAxContainer import *
import time

form_class = uic.loadUiType("ui/main.ui")[0]    # ui 파일을 로드하여 form_class 생성

class MyWindow(QMainWindow, form_class):    # MyWindow 클래스 QMainWindow, form_class 클래스를 상속방아 생성됨
    def __init__(self):
        super().__init__()
        self.setupUi(self)                  # ui 파일 화면 출력

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")        # 키움증권 Open API+ ProgID를 사용하여 생성된 AQxWidget 을 kiwoom 변수에 할당
        self.lineEdit_code.setDisabled(True)
        self.pushButton_search.setDisabled(True)
        self.plainTextEdit_list.setDisabled(True)

        self.pushButton_login.clicked.connect(self.button_login)       # pushButton_login 버튼이 클릭되면 button_login 함수 호출
        self.kiwoom.OnEventConnect.connect(self.event_connect)          # 키움 서버 접속관련 이벤트가 발생할 경우 event_connect 함수 호출

        self.pushButton_search.clicked.connect(self.button_search)
        self.kiwoom.OnReceiveTrData.connect(self.get_tr_baisc_data)



    def auto_trading(self):
        """키움증권 HTS에 등록한 조건검색식에서 검출한 종목을 매수하고
        -2%, +3%에 손절/익절 매도하는 기본적인 자동매매 함수

        :return:
        """
        # callback fn 등록
        self.kw.notify_fn["_on_receive_real_condition"] = self.search_condi

        screen_no = "4000"
        condi_info = self.kw.get_condition_load()
        # {'추천조건식01': '002',
        #'추천조건식02': '000',
        #'급등/상승_추세조건': '001',
        #'Envelop횡단': '003',
        #'스켈핑': '004'}
        for condi_name, condi_id in condi_info.items():
        # 화면번호, 조건식이름, 조건식ID, 실시간조건검색(1)
            self.kw.send_condition(screen_no, condi_name, int(condi_id), 1)
        time.sleep(0.2)

    def search_condi(self, event_data):
        """키움모듈의 OnReceiveRealCondition 이벤트 수신되면 호출되는 callback함수
        이벤트 정보는 event_data 변수로 전달된다.

            ex)
            event_data = {
                "code": code, # "066570"
                "event_type": event_type, # "I"(종목편입), "D"(종목이탈)
                "condi_name": condi_name, # "스켈핑"
                "condi_index": condi_index # "004"
            }
        :param dict event_data:
        :return:
        """
        if event_data["event_type"] == "I":
            if self.stock_account["계좌정보"]["예수금"] < 100000:  # 잔고가 10만원 미만이면 매수 안함
                return
            curr_price = self.kw.get_curr_price(event_data["code"])
            quantity = int(100000 / curr_price)
            self.kw.reg_callback("OnReceiveChejanData", ("조건식매수", "5000"), self.update_account)
            self.kw.send_order("조건식매수", "5000", self.acc_no, 1, event_data["code"], quantity, 0, "03", "")


    def button_login(self):
        ret = self.kiwoom.dynamicCall("CommConnect()")      # 키움 로그인 윈도우를 실행

    def event_connect(self, error_code):
        if error_code == 0:
            self.lineEdit_code.setDisabled(False)
            self.pushButton_search.setDisabled(False)
            self.plainTextEdit_list.setDisabled(False)
            self.plainTextEdit_list.appendPlainText("Login Success")

            account_info = self.kiwoom.dynamicCall("GetLoginInfo(Qstring)", ["ACCNO"])
            self.plainTextEdit_list.appendPlainText("계좌번호: " + account_info.rstrip(';'))
        else:
            self.lineEdit_code.setDisabled(True)
            self.pushButton_search.setDisabled(True)
            self.plainTextEdit_list.setDisabled(True)
            self.plainTextEdit_list.appendPlainText("Login Failed")

    def button_search(self):
        code = self.lineEdit_code.text()
        self.plainTextEdit_list.appendPlainText("종목코드: " + code)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, int, QString", "opt10001_req", "opt10001", 0, "0101")

    def get_tr_baisc_data(self, screen_no, rq_name, tr_code, record_name, prev_next, data_len, error_code, meessage1, message2):
        if rq_name == "opt10001_req":
            name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", tr_code, "", rq_name, 0, "종목명")
            volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", tr_code, "", rq_name, 0, "거래량")
            self.plainTextEdit_list.appendPlainText("종목명: " + name.strip())
            self.plainTextEdit_list.appendPlainText("거래량: " + volume.strip())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()                   # MyWindow 클래스를 생성하여 mywindow 변수에 할당
    mywindow.show()
    app.exec_()