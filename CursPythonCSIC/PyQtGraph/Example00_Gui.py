# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 15:18:09 2020

@author: lucia
"""

from __future__ import print_function
import os

import numpy as np
import time

from PyQt5 import Qt

from pyqtgraph.parametertree import Parameter, ParameterTree

import Trees.SignalConfiguration as SigConfig

class MainWindow(Qt.QWidget):
    ''' Main Window '''
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setFocusPolicy(Qt.Qt.WheelFocus)
        layout = Qt.QVBoxLayout(self)

        self.btnStart = Qt.QPushButton("Start Gen and Adq!")
        layout.addWidget(self.btnStart)
        
#############################SignalConfig##############################
        self.SigParams = SigConfig.SignalConfig(QTparent=self,
                                                name='Signal Configuration')        
        self.Parameters = Parameter.create(name='params',
                                           type='group',
                                           children=(self.SigParams,))
        
#############################GuiConfiguration##############################
        self.Parameters.sigTreeStateChanged.connect(self.on_Params_changed)
        self.treepar = ParameterTree()
        self.treepar.setParameters(self.Parameters, showTop=False)
        self.treepar.setWindowTitle('pyqtgraph example: Parameter Tree')

        layout.addWidget(self.treepar)

        self.setGeometry(550, 10, 300, 700)
        self.setWindowTitle('MainWindow')
        self.btnStart.clicked.connect(self.on_btnStart)

#############################Changes Control##############################
    def on_Params_changed(self, param, changes):
        print("tree changes:")
        for param, change, data in changes:
            path = self.Parameters.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
        print('  parameter: %s' % childName)
        print('  change:    %s' % change)
        print('  data:      %s' % str(data))
        print('  ----------')       
        
#############################START##############################
    def on_btnStart(self):
        self.SignalConfigKwargs = self.SigParams.Get_SignalConf_Params()
        print('SignalConfigKwargs -->', self.SignalConfigKwargs)
#############################MAIN##############################


if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec_()