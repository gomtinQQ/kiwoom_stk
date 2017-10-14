import sys
import time
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from PyQt5.QtWidgets import *
import sqlite3
from pykiwoom.kiwoom import *
import env

MARKET_KOSPI   = 0
MARKET_KOSDAK  = 10

TR_REQ_TIME_INTERVAL = 4
# TR_REQ_TIME_INTERVAL = 2

#####################################################################################################
# STARTDAY은  data을 가져올 때  시작 날짜이다. 즉 모든 data 수집은  STARTDAY을 기준으로 한다.
# 만일 전부 save하고, 다시 update한다면 ,   시간 절약을 위해서  STARTDAY을 최신의 날짜로 바꾸어 주는 것이 좋다.
# 그렇지 않으면,   20010101 부터 시작 할 것이므로.

STARTDAY = "20010101"

# STARTDAY = "20170101"
#####################################################################################################


app = QApplication(sys.argv)

class KiwoomWrapper:
    def __init__(self, kiwoom=None):
        if kiwoom == None :
            self.kiwoom = Kiwoom()
            self.kiwoom.comm_connect()
        else:
            self.kiwoom = kiwoom

    def get_dict_themecode_themelist(self):
        """
        테마코드와 테마명, 그리고 테마코드와 해당 코드들을  dict type으로 반환한다.
        :return:
        """
        listThemecodeThemename = self.kiwoom.get_theme_group_list(0).split(";")
        dictThemecodeThemename = {}
        for ThemecodeThemename in listThemecodeThemename:
            Themecode, Themename = ThemecodeThemename.split("|")
            dictThemecodeThemename[Themecode] = Themename
        dictThemecodelistcode = {}
        for Themecode in dictThemecodeThemename.keys():
            dictThemecodelistcode[Themecode] = self.kiwoom.get_theme_group_code(Themecode).split(";")

        del listThemecodeThemename
        return dictThemecodeThemename, dictThemecodelistcode





    def get_data_opt10081(self, code, date='20161231'):
        """
        최근부터 date 가 지정하는 날짜까지 opt10081을 가져 온다.
        그러나, 만일 이미 받은 data가 있다면,  data.index[-2] 부터, 최근까지의 data을 가져 온다.
        :param code:
        :param date: 최근부터 시작해서 data을 가져오는 마지막 end date임.
        :return:
        """
        try:
            data = pd.read_hdf("../data/hdf/%s.hdf" % code, 'day').sort_index()
            self.start_date = str(data.index[-2])       # data.index 은 날짜형식의 숫자이다.
        except (FileNotFoundError, IndexError, OSError, IOError)  as e:
            # pandas=0.18.1은 OSError, IOError가 난다.
            self.start_date = STARTDAY
        print("get opt10081 data from %s" % self.start_date)
        self.kiwoom.start_date = datetime.strptime(self.start_date, "%Y%m%d")
        self.kiwoom.data_opt10081 = [] * 15
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", date)
        self.kiwoom.set_input_value("수정주가구분", 255)
        self.kiwoom.comm_rq_data("주식일봉차트조회요청", "opt10081", 0, "0101")
        while self.kiwoom.inquiry == '2':
            time.sleep(TR_REQ_TIME_INTERVAL)
            self.kiwoom.set_input_value("종목코드", code)
            self.kiwoom.set_input_value("기준일자", date)
            self.kiwoom.set_input_value("수정주가구분", 255)
            self.kiwoom.comm_rq_data("주식일봉차트조회요청", "opt10081", 2, "0101")
        self.kiwoom.data_opt10081.index = self.kiwoom.data_opt10081.loc[:, '일자']
        return self.kiwoom.data_opt10081.loc[:, ['현재가', '거래량', '거래대금', '시가', '고가', '저가']]

    def get_data_opt10086(self, code, date):
        """
        최근부터 date 가 지정하는 날짜까지 opt10086을 가져 온다.
        그러나, 만일 이미 받은 data가 있다면,  data.index[-2] 부터, 최근까지의 data을 가져 온다.
        :param code:
        :param date: 최근부터 시작해서 data을 가져오는 마지막 end date임.
        :return:
        """
        try:
            data = pd.read_hdf("../data/hdf/%s.hdf" % code, 'day').sort_index()
            self.start_date = str(data.index[-2])
        except (FileNotFoundError, IndexError, OSError, IOError) as e:
            # pandas=0.18.1은 OSError, IOError가 난다.
            self.start_date = STARTDAY
        print("get opt10086 data from %s" % self.start_date)
        self.kiwoom.start_date = datetime.strptime(self.start_date, "%Y%m%d")
        self.kiwoom.data_opt10086 = [] * 23
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("조회일자", date)
        self.kiwoom.set_input_value("표시구분", 1)
        self.kiwoom.comm_rq_data("일별주가요청", "opt10086", 0, "0101")
        while self.kiwoom.inquiry == '2':
            time.sleep(TR_REQ_TIME_INTERVAL)
            self.kiwoom.set_input_value("종목코드", code)
            self.kiwoom.set_input_value("조회일자", date)
            self.kiwoom.set_input_value("표시구분", 1)
            self.kiwoom.comm_rq_data("일별주가요청", "opt10086", 2, "0101")
        self.kiwoom.data_opt10086.index = self.kiwoom.data_opt10086.loc[:, '일자']
        return self.kiwoom.data_opt10086

    def get_codelist_by_market(self, market):
        """
        market의 code list을 반환한다.
        :param market:
        :return:
        """
        return self.kiwoom.get_codelist_by_market(market)


    def save_code_jongmok_to_hdf(self):
        """
        code을  index으로 하는 종목이름을 생성하여, dataframe을 만들고, 이를
        hdf으로 저장한다.
        :param code: 종목코드
        :return: 성공여부
        """
        try:
            kospi_codes = self.get_codelist_by_market(MARKET_KOSPI)
            kosdak_codes = self.get_codelist_by_market(MARKET_KOSDAK)
            listcode = kospi_codes + kosdak_codes
            listcode.sort()

            listjongmok = []
            for code in listcode :
                listjongmok.append(self.kiwoom.get_master_code_name(code))
            pdcodejongmok = pd.DataFrame(listjongmok, index=listcode, columns=["jongmok"])

            pdcodejongmok.to_hdf(env.Env["code_name_hdf"], "codename", mode='w')
            return True
        except:
            return False



if __name__ == '__main__':
    kiwoom_wrapper = KiwoomWrapper()
    kiwoom_wrapper.save_code_jongmok_to_hdf()
    print("Job Done")
