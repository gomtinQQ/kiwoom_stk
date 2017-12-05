# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
#date:
#---------------------------------------------------------
from __future__ import (absolute_import, division, print_function, unicode_literals)

import argparse
import pandas as pd
import collections
import time

import concurrent.futures
import numpy as np
import os

def csvfilter_rate(clsvar):
    """
    clsvar.filein 에서 "rate" 이 있는 row만  clsvar.fileout 에 저장
    :param clsvar: 
    :return: 
    """
    fin = open(clsvar.filein)
    fout = open(clsvar.fileout, "w" )

    # read head and save to fout
    # line = fin.readline()
    # fout.write(line)

    count = 0

    for line in fin :
        count += 1
        if count % 1000 == 0 :
            print(".", end="")

        if line.split(",")[5] == "rate" :
            fout.write(line)

    fin.close()
    fout.close()


def makeHDFfromCSV(clsvar):
    """
    head : code,mashort,malong,volperiod,volmulti,rate,profitrate 을 가진 CSV file을 
    hdf 으로 만들어 저장한다.
    
    csv file size가 너무 크면, 이를  200000 건으로 분리해서 저장한다.
    :param clsvar: 
    :return: 
    """
    fincsv = open(clsvar.filein)
    listhead = fincsv.readline().strip().split(",")
    listhead = ["code","mashort","malong","volperiod","volmulti","profitrate"]
    df = pd.DataFrame(columns=listhead)
    csvindex = 0
    hdfindex = 0

    hdffilesufindex = 0
    hdffilebase = clsvar.fileout.split(".")[0]
    hdffileext = clsvar.fileout.split(".")[1]


    for item in fincsv :

        listvalue = item.strip().split(",")

        # d = collections.OrderedDict(zip(listhead, listvalue))
        # d["mashrot"] = int(d["mashrot"])
        # d["mashrot"] = int(d["malong"])
        # d["mashrot"] = float(d["lastvalue"])
        # d["mashrot"] = int(d["lenlist"])
        # d["mashrot"] = float(d["mean"])
        # d["mashrot"] = float(d["var"])
        # d["mashrot"] = float(d["cdf"])
        # d["mashrot"] = float(d["pvalue"])
        # d["mashrot"] = int(d["volperiod"])
        # d["mashrot"] = int(d["volmulti"])
        # df.loc[csvindex] = list(d.values())

        listtemp = []
        listtemp.append(listvalue.pop(0))   #code
        listtemp.append(int(listvalue.pop(0)))  # mashrot
        listtemp.append(int(listvalue.pop(0)))  # malong
        # listtemp.append(float(listvalue.pop(0)))  # lastvalue
        # listtemp.append(int(listvalue.pop(0)))  # lenlist
        # listtemp.append(float(listvalue.pop(0)))  # mean
        # listtemp.append(float(listvalue.pop(0)))  # var
        # listtemp.append(float(listvalue.pop(0)))  # cdf
        # listtemp.append(float(listvalue.pop(0)))  # pvalue
        listtemp.append(int(listvalue.pop(0)))  # volperiod
        listtemp.append(float(listvalue.pop(0)))  # volmulti
        listvalue.pop(0)  # rate
        listtemp.append(float(listvalue.pop(0)))  # profitrate

        df.loc[hdfindex] = listtemp

        csvindex += 1
        hdfindex += 1

        if (csvindex % 1000 ) == 0 :
            print("csvindex=%s"%csvindex)

        if hdfindex == 100000 :
            newhdffile = hdffilebase + "_%04d"%hdffilesufindex + "." + hdffileext
            df.to_hdf(newhdffile, key="day")
            hdffilesufindex += 1
            print("new hdf file")

            # create new dataframe
            del df
            df = pd.DataFrame(columns=listhead)
            hdfindex = 0

    newhdffile = hdffilebase + "_%04d" % hdffilesufindex + "." + hdffileext
    df.to_hdf(newhdffile, key="day")
    print("finished...")


def makeHDFfromCSV_process(npa, npb) :
    print("%d is started"%(os.getpid()))
    for i in range(10000) :
        npa = npa * npb

    print("%d is ended" % (os.getpid()))


def makeHDFfromCSV_concurrent(clsvar):
    """
    multiprocess api인 concurrent을 이용하여  고속으로 csv을 hdf으로 처리한다.
    단 makeHDFfromCSV 처럼,  200000 개를 개별 hdf으로 저장한다.
    :param clsvar: 
    :return: 
    """

    listfuture = []


    # with 구문안에서 해야만 제대로 multi process가 된다.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for i in range(100):
            npa = np.random.rand(50,100,100)
            npb = np.random.rand(50,100,100)
            future = executor.submit(makeHDFfromCSV_process, npa,npb )
            listfuture.append(future)

    # check if process is finished.
    while(True):
        listdone = [ future.done() for future in listfuture]
        if all(listdone) :
            print("all jobs is done")
            break
        print("Sleep ...")
        time.sleep(30)


def CalMeanToCSV_try1(clsvar):
    """
    종가이평선 2개, 거래량 이평선 2개에 의한  profitrate을 평균내여 fileout 에 csv format으로 저장한다.  
    mashort, malong, volperiod, volmulti, profitrate 의 5개 항목을  numpy에 넣어서
    mean을 구하고, 파일으로 출력한다.

    :param clsvar:
    :return:

    maPeriodShort=range(9,15), maPeriodLong=range(41, 50),
    VolumeMultiple=[1.5, 2, 3, 4, 5, 8, 10, 15, 20], maVolPeriod=[30,40,50,60]
    """

    indexshort = dict(zip(range(9,15), range(len(range(9,15)))))
    indexlong = dict(zip(range(41, 50), range(len(range(41, 50)))))
    listvolmulti = [1.5, 2., 3., 4., 5., 8., 10., 15., 20.]
    listvolperoid = [30,40,50,60]
    indexvolm = dict(zip(listvolmulti, range(len(listvolmulti))))
    indexvolp = dict(zip(listvolperoid, range(len(listvolperoid))))

    npsum = np.zeros((len(indexvolp), len(indexvolm),len(indexlong),len(indexshort)))
    npcount = np.zeros((len(indexvolp), len(indexvolm), len(indexlong), len(indexshort)))


    fin = open(clsvar.filein)
    listhead = fin.readline().strip().split(",")
    listhead = ["code", "mashort", "malong", "volperiod", "volmulti", "profitrate"]

    cvsindex = 0
    for line in fin:
        code, mashort, malong, volperiod, volmulti, rate, profitrate = line.strip().split(",")
        mashort = int(mashort)
        malong = int(malong)
        volperiod = int(volperiod)
        volmulti = float(volmulti)
        profitrate = float(profitrate)

        npsum[indexvolp[volperiod], indexvolm[volmulti], indexlong[malong],indexshort[mashort]  ] += profitrate
        npcount[indexvolp[volperiod], indexvolm[volmulti], indexlong[malong], indexshort[mashort]] += 1
        cvsindex += 1
        if (cvsindex % 10000) == 0 :
            print("csvindex = %d"% cvsindex)

    fin.close()
    npmean = npsum / npcount

    # open(clsvar.fileout, "w").write(str(npmean))
    fout = open(clsvar.fileout, "w")

    #write head to file
    listhead = ["volperiod", "volmulti", "malong", "mashort", "profitrate", "category"]
    fout.write( ",".join(listhead) + "\n" )


    indexshort = dict(zip(range(len(range(9, 15))), range(9, 15) ))
    indexlong = dict(zip(range(len(range(41, 50))), range(41, 50) ))
    indexvolm = dict(zip(range(len(listvolmulti)), listvolmulti ))
    indexvolp = dict(zip(range(len(listvolperoid)), listvolperoid ))

    for indexp in range(len(indexvolp )) :
        for indexm in range(len(indexvolm)) :
            for indexl in range(len(indexlong)) :
                for indexs in range(len(indexshort)) :
                    fout.write("%d,%.2f,%d,%d,%.5f,profitmean\n"%(
                        indexvolp[indexp],indexvolm[indexm], indexlong[indexl], indexshort[indexs],
                        npmean[indexp,indexm,indexl,indexs]  ) )

    for indexp in range(len(indexvolp)):
        for indexm in range(len(indexvolm)):
            for indexl in range(len(indexlong)):
                for indexs in range(len(indexshort)):
                    fout.write("%d,%.2f,%d,%d,%.5f,profitcount\n" % (
                    indexvolp[indexp], indexvolm[indexm], indexlong[indexl], indexshort[indexs],
                    npcount[indexp, indexm, indexl, indexs]))

    fout.close()


def CalMeanToCSV_try2(clsvar):
    """
    종가이평선 2개, 거래량 이평선 2개에 의한  profitrate을 평균내여 fileout 에 csv format으로 저장한다.  
    mashort, malong, volperiod, volmulti, profitrate 의 5개 항목을  numpy에 넣어서
    mean을 구하고, 파일으로 출력한다.

    :param clsvar:
    :return:

    maPeriodShort=[11,12,13,15,17,19,21], maPeriodLong=[47,49,51,53,55,57,9],
    VolumeMultiple=[15,17,19,21,23,25,30], maVolPeriod=[29,31,33,35,37,39,41,43,45,47]
    """
    listPeriodShort = [11, 12, 13, 15, 17, 19, 21]
    listPeriodLong = [47, 49, 51, 53, 55, 57, 9]
    listvolmulti = [15,17,19,21,23,25,30]
    listvolperoid = [29,31,33,35,37,39,41,43,45,47]

    indexshort = dict(zip(listPeriodShort, range(len(listPeriodShort))))
    indexlong = dict(zip(listPeriodLong, range(len(listPeriodLong))))
    indexvolm = dict(zip(listvolmulti, range(len(listvolmulti))))
    indexvolp = dict(zip(listvolperoid, range(len(listvolperoid))))

    npsum = np.zeros((len(indexvolp), len(indexvolm),len(indexlong),len(indexshort)))
    npcount = np.zeros((len(indexvolp), len(indexvolm), len(indexlong), len(indexshort)))


    fin = open(clsvar.filein)
    listhead = fin.readline().strip().split(",")
    listhead = ["code", "mashort", "malong", "volperiod", "volmulti", "profitrate"]

    cvsindex = 0
    for line in fin:
        code, mashort, malong, volperiod, volmulti, rate, profitrate = line.strip().split(",")
        mashort = int(mashort)
        malong = int(malong)
        volperiod = int(volperiod)
        volmulti = int(volmulti)
        profitrate = float(profitrate)

        npsum[indexvolp[volperiod], indexvolm[volmulti], indexlong[malong],indexshort[mashort]  ] += profitrate
        npcount[indexvolp[volperiod], indexvolm[volmulti], indexlong[malong], indexshort[mashort]] += 1
        cvsindex += 1
        if (cvsindex % 10000) == 0 :
            print("csvindex = %d"% cvsindex)

    fin.close()
    npmean = npsum / npcount

    # open(clsvar.fileout, "w").write(str(npmean))
    fout = open(clsvar.fileout, "w")

    #write head to file
    listhead = ["volperiod", "volmulti", "malong", "mashort", "profitrate", "category"]
    fout.write( ",".join(listhead) + "\n" )

    indexshort = dict(zip(range(len(listPeriodShort)), listPeriodShort ))
    indexlong = dict(zip(range(len(listPeriodLong)), listPeriodLong ))
    indexvolm = dict(zip(range(len(listvolmulti)), listvolmulti ))
    indexvolp = dict(zip(range(len(listvolperoid)), listvolperoid ))



    for indexp in range(len(indexvolp )) :
        for indexm in range(len(indexvolm)) :
            for indexl in range(len(indexlong)) :
                for indexs in range(len(indexshort)) :
                    fout.write("%d,%.2f,%d,%d,%.5f,profitmean\n"%(
                        indexvolp[indexp],indexvolm[indexm], indexlong[indexl], indexshort[indexs],
                        npmean[indexp,indexm,indexl,indexs]  ) )

    for indexp in range(len(indexvolp)):
        for indexm in range(len(indexvolm)):
            for indexl in range(len(indexlong)):
                for indexs in range(len(indexshort)):
                    fout.write("%d,%.2f,%d,%d,%.5f,profitcount\n" % (
                    indexvolp[indexp], indexvolm[indexm], indexlong[indexl], indexshort[indexs],
                    npcount[indexp, indexm, indexl, indexs]))

    fout.close()


if __name__ == "__main__":
    cmdlineopt = argparse.ArgumentParser(description='filter row data from csv file ')
    cmdlineopt.add_argument('-i', action="store", dest="filein", default='filein.csv', help='CSV fileanme to input')
    cmdlineopt.add_argument('-o', action="store", dest="fileout",  default='fileout.csv', help='CSV fileanme to output')

    clsvar = cmdlineopt.parse_args()
    # makeHDFfromCSV(clsvar)
    # csvfilter_rate(clsvar)
    # makeHDFfromCSV_concurrent(clsvar)
    # CalMeanToCSV_try1(clsvar)
    CalMeanToCSV_try2(clsvar)