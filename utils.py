# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
#---------------------------------------------------------

import env
import os
from pykiwoom.kiwoom import *
import pandas as pd
from pandas import DataFrame

def convert_code_to_종목이름(code, usekiwoom):
    """
    hdf을 이용하여 code 을 종목이름 으로 변환하여 반환한다.
    만일 hdf가 없을 경우, usekiwoom 의 BOOL에 따라,
    usekiwoom 을 이용한다.
    :param code:
    :param usekiwoom:  True 이면 Kiwoom 이용할 수 도  있다.
    :return: 종목이름
    """

    hdffilename = env.Env["code_name_hdf"]
    if os.path.exists(hdffilename) == False :
        if usekiwoom == True:
            kiwoom =  Kiwoom()
            kiwoom.comm_connect()
            return kiwoom.get_master_code_name(code)
        else:
            print("can't convert")
            return ""
    else:
        # hdf 을 이용한다.
        try:
            df = pd.read_hdf(hdffilename, "codename")
            return df.loc[code, "jongmok"]
        except:
            print("error while openning hdf")
            return ""


if __name__ == "__main__" :
    pass