import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QAxContainer import *

form_class = uic.loadUiType("ui/main.ui")[0]    # ui 파일을 로드하여 form_class 생성

class MyWindow(QMainWindow, form_class):    # MyWindow 클래스 QMainWindow, form_class 클래스를 상속방아 생성됨
    def __init__(self):
        super().__init__()
        self.setupUi(self)                  # ui 파일 화면 출력

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")        # 키움증권 Open API+ ProgID를 사용하여 생성된 AQxWidget 을 kiwoom 변수에 할당
        self.lineEdit_inputCode.setDisabled(True)
        self.pushButton_search.setDisabled(True)
        self.plainTextEdit_list.setDisabled(True)

        self.pushButton_login.clicked.connect(self.button_login)       # pushButton_login 버튼이 클릭되면 button_login 함수 호출
        self.kiwoom.OnEventConnect.connect(self.event_connect)          # 키움 서버 접속관련 이벤트가 발생할 경우 event_connect 함수 호출

        self.pushButton_search.clicked.connect(self.button_search)
        self.kiwoom.OnReceiveTrData.connect(self.get_tr_baisc_data)

    def button_login(self):
        ret = self.kiwoom.dynamicCall("CommConnect()")      # 키움 로그인 윈도우를 실행

    def event_connect(self, error_code):
        if error_code == 0:
            self.lineEdit_inputCode.setDisabled(False)
            self.pushButton_search.setDisabled(False)
            self.plainTextEdit_list.setDisabled(False)
            self.plainTextEdit_list.appendPlainText("Login Success")

            account_info = self.kiwoom.dynamicCall("GetLoginInfo(Qstring)", ["ACCNO"])
            self.plainTextEdit_list.appendPlainText("계좌번호: " + account_info.rstrip(';'))
        else:
            self.lineEdit_inputCode.setDisabled(True)
            self.pushButton_search.setDisabled(True)
            self.plainTextEdit_list.setDisabled(True)
            self.plainTextEdit_list.appendPlainText("Login Failed")

    def button_search(self):
        code = self.lineEdit_inputCode.text()
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