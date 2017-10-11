# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
#---------------------------------------------------------
from pywinauto import application
import pywinauto.findwindows as findwin
import time
import psutil, os

# 아래의 code들은  다음의 url을  보고서  만들었다.
# http://pywinauto.readthedocs.io/en/latest/getting_started.html# 을 참조하자.

def click_kiwoom_pop():
    """
    재접속 안내 pop-up창이 뜨면, 확인 버튼을 눌러 준다.
    :return:
    """
    found = False
    listtitle = [u"[HTS 재접속 안내]", u"안녕하세요. 키움증권 입니다.", u"KHOpenAPI"]
    for wintitle in listtitle :
        try:
            app = application.Application()
            win = findwin.find_window(title=wintitle)
            kiwoomapp = app.connect(handle = win)
            kiwoomspec = kiwoomapp.window(title=wintitle)
            kiwoomspec.child_window(title="확인").click()
            print("%s : Pop-up found : %s"%(time.asctime(), wintitle) )
            found = True
        except:
            pass
    return found

def find_procs_id_by_pname_param(pname, param):
    """
    program, param으로 해당하는 process의 ID을 리턴한다.
    :param pname: program이름
    :param param: parameter
    :return: pid
    """

    for p in psutil.process_iter():
        try:
            listcmdline = p.cmdline()
            if len(listcmdline) >= 2 and "python" in listcmdline[0] and param in listcmdline[1]:
                return p.pid
        except (psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except psutil.NoSuchProcess:
            continue
    return 0

def insert_command_on_cmdline(wintitle, strcmd):
    strcmd = strcmd + "\n"

    try:
        app = application.Application()
        win = findwin.find_window(title=wintitle)
        cmdapp = app.connect(handle=win)
        cmdspec = cmdapp.window(title=wintitle)
        cmdspec.wrapper_object().type_keys("^c")
        time.sleep(5)
        cmdspec.wrapper_object().send_chars(strcmd)
    except Exception as e :
        print(e)
        pass


if __name__ == "__main__" :
    cmdline0 = "C:\\Anaconda3_32\\python.exe "
    cmdline1 = "save_data.py"
    # cmdline1 = "test.py"

    wintitle = "관리자: C:\\Windows\\system32\\cmd.exe"
    print("command : " + cmdline0 + cmdline1)

    timesleep = 300

    while(True) :
        found =  click_kiwoom_pop()
        if found == True :
            # kiwomm pop() was found
            time.sleep(600)

        if find_procs_id_by_pname_param(cmdline0, cmdline1) == 0 or found == True:
            # no processing
            print("No Processing Found, Execute command again")
            insert_command_on_cmdline(wintitle, cmdline0 + cmdline1)

        print("sleep %ssec"%timesleep)
        time.sleep(timesleep)

