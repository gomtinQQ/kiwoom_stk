# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
#---------------------------------------------------------

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas_datareader.data as web
import pandas as pd
from pandas import Series, DataFrame
from pykiwoom.wrapper import *
from pykiwoom.kiwoom import *
import env
import os
import utils
import pyalgo
from  datetime import datetime


class MyWindow(QWidget):
    def __init__(self, code):
        super().__init__()
        self.code = code
        self.setupUI()

    def setupUI(self):
        self.setGeometry(600, 200, 1200, 600)
        self.setWindowTitle("PyChart Viewer v0.1")
        self.setWindowIcon(QIcon('icon.png'))

        # get the DataFrame for code .
        df = pyalgo.get_dataframe_with_code(self.code)
        self.data = pyalgo.add_이동평균선_to_dataframe(df, [5,20])

        listcolumns = list(self.data)
        jongmok = utils.convert_code_to_종목이름(self.code, False)

        # right layout widget들
        self.lineEdit = QLineEdit()
        self.lineEdit.setText(jongmok)
        self.pushButton = QPushButton("차트그리기")
        self.pushButton.clicked.connect(self.pushButtonClicked)



        # left layout widget들
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

        # left Layout and adding widget
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.canvas)

        # Right Layout and adding widget
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.pushButton)

        self.listwcheck = []
        for column in listcolumns:
            wcheck = QCheckBox(column, self)
            rightLayout.addWidget(wcheck)
            self.listwcheck.append(wcheck)

        rightLayout.addStretch(1)

        # 전체 Layout
        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    def pushButtonClicked(self):
        ax = self.fig.add_subplot(111)
        # self.data의 개수가 많아서  보기가 불편하다. 이를 줄인다.
        data = self.data.tail(300)
        # data.index의 수자 형식에서  날짜형식으로 변환해 준다.
        index = pd.Series([datetime.strptime(str(aa),"%Y%m%d") for aa in data.index ])

        for wcheck in self.listwcheck :
            if wcheck.isChecked() == True:
                column = wcheck.text()
                ax.plot(index, data[column], label=column)


        ax.legend(loc='upper right')
        ax.grid()

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow("004000")
    window.show()

    app.exec_()