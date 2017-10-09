# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
#---------------------------------------------------------

# 각 control에 대한 이름을 알고 싶으면, 다음을 참조.
# https://github.com/pywinauto/SWAPY/releases
# https://github.com/jaehyek/gui-inspect-tool

# pywinauto에 대해 알고 싶은면 다음을 참조한다.
# http://pywinauto.readthedocs.io/en/latest/index.html

# 주의 :
# 1. 실행시 반드시 관리자 권한하에서 실행.
# 2. 실행시 anaconda-32bit python console에서 실행.



from pywinauto.application import Application
import time
import os

def update_version():
    # 목적 : kiwoom의 version update하기 위함.

    # Account : id은 이미 지정되어 있으므로, id password, 공인인증서 password 을 지정을 한다.
    account = []
    with open("../data/account.txt", 'r') as f:
        account = f.readlines()

    # split the newline
    account = [ aa.strip() for aa in account]

    app = Application().Start(cmd_line=u"C:\\51.키움증권\\KiwoomFlash3\\bin\\nkministarter.exe")
    mainframe = app[u'번개3 login']
    mainframe.Wait('ready')
    time.sleep(2)
    mainframe.Edit2.set_text(account[0])

    time.sleep(2)

    mainframe.Edit3.set_text(account[1])
    time.sleep(2)

    mainframe.Button0.Click()
    time.sleep(30)
    app.Kill_()

    # 업데이트가 완료될 때 까지 대기
    while True:
        time.sleep(5)
        with os.popen('tasklist /FI "IMAGENAME eq nkmini.exe"') as f:
            lines = f.readlines()
            if len(lines) >= 3:
                print("found the nkmini.exe")
                break

    # 번개3 종료
    time.sleep(30)
    print("taskill nkmini.exe")
    os.system("taskkill /im nkmini.exe")

if __name__ == "__main__" :
    update_version()
