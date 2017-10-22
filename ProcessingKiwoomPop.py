# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
#---------------------------------------------------------
from pywinauto import application
import pywinauto.findwindows as findwin
import time
import psutil, os
from datetime import datetime as dt

# 아래의 code들은  다음의 url을  보고서  만들었다.
# http://pywinauto.readthedocs.io/en/latest/getting_started.html# 을 참조하자.

def click_kiwoom_pop():
    """
    재접속 안내 pop-up창이 뜨면, 확인 버튼을 눌러 준다.
    :return:
    """
    found = False
    listtitle = ["[HTS 재접속 안내]", "안녕하세요. 키움증권 입니다.", "KHOpenAPI", "조회횟수 제한 : -209", "opstarter"]
    for wintitle in listtitle :
        try:
            app = application.Application()
            win = findwin.find_window(title=wintitle)
            kiwoomapp = app.connect(handle = win)
            kiwoomspec = kiwoomapp.window(title=wintitle)
            kiwoomspec.child_window(title="확인").set_focus()
            kiwoomspec.child_window(title="확인").click()
            print("%s : Pop-up found : %s"%(time.asctime(), wintitle) )
            found = True
            time.sleep(600)
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

def insert_command_on_cmdline(wintitle, strcmd, cmdspec=None):
    """
    wintitle을 가진 window을 찾아서 strcmd을 수행시킨다.
    wintitle은 단지 cmd.exe을 수행한 이후,  process가 없는 빈 도스창이다.
    만일 cmdspec이 있으면, 이를 사용한다.
    :param wintitle:
    :param strcmd:
    :param cmdspec: if not None, pywinauto windows spec
    :return:
    """
    strcmd = strcmd + "\n"
    try:
        if cmdspec == None:
            app = application.Application()
            win = findwin.find_window(title=wintitle)
            cmdapp = app.connect(handle=win)
            cmdspec = cmdapp.window(title=wintitle).wrapper_object()

        cmdspec.send_keystrokes(strcmd)
    except Exception as e :
        print(e)
        pass

def is_if_receiving_opt10086_data():
    """
    save_data.py을 실행하고, 가끔 opt10086 data가 오지 않는 경우가 있다.
    특히 주식 장이 열린 시간에서 이런 일들이 일어난다.
    이 때, 해당 process을 kill하고 다시 실행시켜 준다.
    여기서는 kiwoom.log의 마지막 opt10086 n line의 마지막 시간을 보고,
    10분 이내인지 판단한다.
    :return: False(not receiving ) or True(reveiving)
    """
    filelog = ".\\kiwoom.log"

    #먼저 기본적으로 4096byte을 읽어 온다. 미리 size을 확인한다.
    filesize = os.path.getsize(filelog)
    if filesize < 5000 :
        return True

    try:
        f = open(filelog, "r")
        f.seek(filesize-4096, 0)
        listlog = f.readlines()
        strlasttime = ""
        for log in listlog :
            if "opt10086" not in log :
                continue
            strlasttime = log.split(",")[0]
        if len(strlasttime) == 0 :
            return False
        dtlasttime = dt.strptime(strlasttime, "%Y-%m-%d %H:%M:%S")
        if (dt.now() - dtlasttime).seconds >= 600 :
            return False
        else:
            return True
    except:
        print("can't read logfile")
        return True


if __name__ == "__main__" :
    cmdline0 = "C:\\Anaconda3_32\\python.exe "
    cmdline1 = "save_data.py"

    # wintitle = "관리자: C:\\Windows\\system32\\cmd.exe"
    wintitle = "관리자: Windows PowerShell ISE (x86)"
    print("command : " + cmdline0 + cmdline1)
    timesleep = 300
    cmdwin = "PowerShell_ISE.exe"

    # 주의 사항 :
    # 1. 이 스크립트를 실행시, 반드시, "save_data.py" 가 있는 dir에서 수행한다.
    # 2. "C:\\Anaconda3_32\\python.exe " 을 이용하여 "save_data.py"  스크립트를 수행한다.

    app = application.Application().start(cmdwin)
    cmdspec = app.PowerShellISE.wrapper_object()

    while(True) :
        if click_kiwoom_pop() == True :
            print("%s : pop was found"%(dt.now()))
            continue

        while(True):
            proc_id = find_procs_id_by_pname_param(cmdline0, cmdline1)
            if proc_id != 0 :
                break
            print("%s : No Processing Found, Execute command again" % (dt.now()))
            insert_command_on_cmdline(wintitle, cmdline0 + cmdline1, cmdspec)
            time.sleep(5)

        if  is_if_receiving_opt10086_data() == False :
            # process은 살아 있는데, data을 받지 않고 있다면,  kill process
            psutil.Process(proc_id).terminate()
            print("%s : killing process"%(dt.now()))
            time.sleep(5)
            continue


        print("sleep %sec"%timesleep)
        time.sleep(timesleep)

