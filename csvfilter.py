# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
#date:
#---------------------------------------------------------
from __future__ import (absolute_import, division, print_function, unicode_literals)

import argparse

def csvfilter(clsvar):
    fin = open(clsvar.filecsvin)
    fout = open(clsvar.filecsvout, "w", encoding='utf-8')

    # read head and save to fout
    line = fin.readline()
    fout.write(line)

    for line in fin :
        pvalue = float(line.strip().split(",")[-1])
        if pvalue >= 0.05 :
            continue
        fout.write(line)

    fin.close()
    fout.close()


if __name__ == "__main__":
    cmdlineopt = argparse.ArgumentParser(description='filter row data from csv file ')
    cmdlineopt.add_argument('-i', action="store", dest="filecsvin", default='filecsvin.csv', help='CSV fileanme to input')
    cmdlineopt.add_argument('-o', action="store", dest="filecsvout",  default='filecsvout.csv', help='CSV fileanme to output')

    clsvar = cmdlineopt.parse_args()
    csvfilter(clsvar)