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


def get_list_code():
    try:
        hdffilename = env.Env["code_name_hdf"]
        df = pd.read_hdf(hdffilename, "codename")
        listcode =  df.index.tolist()

        # delete the empty code string
        listret = []
        for code in listcode:
            if len(code) > 0 :
                listret.append(code)
        del listcode
        return listret
    except:
        print("error while openning hdf")
        return []


def get_dataframe_with_code(code):
    """
    code hdf으로 부터 dataframe을 읽어 온다.
    :param code:
    :return:
    """

    # get the DataFrame for code .
    hdffilename = env.Env["data_hdf_dir"] + "/%s.hdf" % (code)
    if os.path.exists(hdffilename) == False:
        raise Exception("No hdf file")

    data = pd.read_hdf(hdffilename, 'day').sort_index()

    #만일 거래량이 없으면, 해당 항목을 제거한다.
    data = data[data["거래량"] > 0 ]

    return data

def add_이동평균선_to_dataframe(df, listma):
    """
    dataframe을 받아서  현재가를 기준으로 이동 평균선을 구해서 dataframe에 column으로 넣어준다.
    :param df: dataframe
    :param listma: 원하는 이동평균선의 일자 list
    :return: dataframe
    """

    # 먼저 dataframe에 "현재가" column이 있는지 확인
    if  "현재가" not in list(df) :
        raise Exception("No 현재가 column name in dataframe")

    # lista에 있는 원소들이 전부 정수인지 확인한다.from
    if all([isinstance(aa, int) for aa in listma ]) == False :
        raise Exception("Not all interger")

    for ma in listma :
        dfma = df["현재가"].rolling(window=ma).mean()
        df["MA%s"%ma] = dfma

    return df


if __name__ == "__main__" :
    df = get_dataframe_with_code("005440")
    df = add_이동평균선_to_dataframe(df, [5,20])

    print(df["MA5"].tail())
    print(df["MA20"].tail())