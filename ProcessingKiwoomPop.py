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

    listtitle = [u"[HTS 재접속 안내]", u"안녕하세요. 키움증권 입니다.", u"KHOpenAPI", u"KHOpenAPI" ]
    for wintitle in listtitle :
        try:
            app = application.Application()
            win = findwin.find_window(title=wintitle)
            time.sleep(600)
            kiwoomapp = app.connect(handle = win)
            kiwoomdlg = kiwoomapp.window(title=wintitle)
            kiwoomdlg.child_window(title="확인").click()
            print("___ Pop-up found ___")
        except:
            print("Pop-up was not found: %s"%wintitle )
            pass

def find_procs_id_by_name_param(pname, param):
    "Return a list of processes matching 'name'."

    for p in psutil.process_iter():
        name, exe, cmdline = "", "", []
        try:
            name = p.name()
            cmdline = p.cmdline()
            exe = p.exe()
        except (psutil.AccessDenied, psutil.ZombieProcess):
            pass
        except psutil.NoSuchProcess:
            continue
        if pname == name and  param in  cmdline[0] :
            return p.pid
    return 0


if __name__ == "__main__" :
    while(True) :
        listprocessname = [p.name() for p in psutil.process_iter()]
        countpython = listprocessname.count("python.exe")

        psutil.Process(os.getpid()).cmdline()
        # ['C:\\Python26\\python.exe', '-O']

        time.sleep(60)
        click_kiwoom_pop()
