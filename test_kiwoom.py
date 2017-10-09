from pykiwoom.kiwoom import *
from pykiwoom.wrapper import *
from pprint import pprint

MARKET_KOSPI   = 0
MARKET_KOSDAK  = 10

class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()
        self.wrapper = KiwoomWrapper(self.kiwoom)
        self.get_code_list()

    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_codelist_by_market(MARKET_KOSPI)
        self.kosdak_codes = self.kiwoom.get_codelist_by_market(MARKET_KOSDAK)
        print("the count of kospi is  %s"% (len(self.kospi_codes)))
        print("the count of kosdak is  %s" % (len(self.kosdak_codes)))

    def get_code_name(self, code ):
        return self.kiwoom.get_master_code_name(code)

if __name__ == '__main__':
    pymon = PyMon()

    dictThemecodeThemename, dictThemecodelistcode = pymon.wrapper.get_dict_themecode_themelist()

    pprint(dictThemecodelistcode)
