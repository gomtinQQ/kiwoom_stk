# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
#---------------------------------------------------------

import pandas as pd
import env
import os

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