# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
#---------------------------------------------------------
from pywinauto import application
import pywinauto.findwindows as findwin
import time
import psutil

# 아래의 code들은  다음의 url을  보고서  만들었다.
# http://pywinauto.readthedocs.io/en/latest/getting_started.html# 을 참조하자.

def click_kiwoom_pop():
    """
    재접속 안내 pop-up창이 뜨면, 확인 버튼을 눌러 준다.
    :return:
    """
    found = False
    listtitle = [u"[HTS 재접속 안내]", u"안녕하세요. 키움증권 입니다.", u"KHOpenAPI" ]
    for wintitle in listtitle :
        try:
            app = application.Application()
            win = findwin.find_window(title=wintitle)
            kiwoomapp = app.connect(handle = win)
            kiwoomspec = kiwoomapp.window(title=wintitle)
            kiwoomspec.child_window(title="확인").click()
            print("Pop-up was found: %s" % wintitle)
            found = True
        except:
            pass
    return found

def find_procs_id_by_pname_param(pname, param):
    "Return a list of processes matching 'name'."

    for p in psutil.process_iter():
        try:
            name = p.name()
            listcmdlist = p.cmdline()
            if len(listcmdlist) >= 2 and "python" in listcmdlist[0] and  param in  listcmdlist[1] :
                return p.pid
        except (psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except psutil.NoSuchProcess:
            continue

    return 0

def input_command_to_cmd_win(wintitle, strcmd):
    """
    이 함수는 이미 windows 화면상에 "Command Prompt"가 실행이 된 상태에서 
    인자로 받은 strcmd을 실행하는 것이다.
    :param strcmd:  실행하고자 하는 command string.
    :return: 없음.
    """

    strcmd = strcmd + "\n"
    try:
        app = application.Application()
        win = findwin.find_window(title=wintitle)
        cmdapp = app.connect(handle=win)
        cmdspec = cmdapp.window(title=wintitle)
        cmdspec.wrapper_object().send_chars(strcmd)
    except:
        print("Window was not found: %s" % wintitle)
        pass


if __name__ == "__main__" :
    pname = "c:\\anaconda3_32\\python.exe"
    param = "test.py"

    strcmd = pname + " " + param
    wintitle = u"관리자: Command Prompt"

    input_command_to_cmd_win(wintitle, strcmd)

    while(True) :
        if click_kiwoom_pop() == True :
            # 경고 창을 click하고, 10 분간 여유를 둔다.
            time.sleep(600)

        pid = find_procs_id_by_pname_param(pname, param)
        if ( pid == 0 ) :
            # pname + param 이 실행되지 않으면, 다시 실행시킨다.
            print("command process was stopped, execute again")
            input_command_to_cmd_win(wintitle, strcmd)

        time.sleep(60)

