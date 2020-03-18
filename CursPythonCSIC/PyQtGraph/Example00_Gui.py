# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 15:18:09 2020

@author: lucia
"""

from __future__ import print_function
import os

import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.signal import welch

from PyQt5 import Qt

from pyqtgraph.parametertree import Parameter, ParameterTree

import Trees.SignalConfiguration as SigConfig
import ThreadsAndFunctions.SignalGeneration as SigGen

import PyqtTools.PlotModule as PltMod

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
        
        self.threadGeneration = None
        self.threadPlotter = None
        self.threadPsdPlotter = None

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
        
#############################Changes Emits##############################
#SiCualquierParametro de la carrier o moduladora cambia, llamar directamente a 
        #GenCarrier y GenModulation
        
#############################START##############################
    def on_btnStart(self):
        if self.threadGeneration is None:
            self.SignalConfigKwargs = self.SigParams.Get_SignalConf_Params()
            print('SignalConfigKwargs -->', self.SignalConfigKwargs)
            self.threadGeneration = SigGen.GenerationThread(self.SignalConfigKwargs)
            self.threadGeneration.NewGenData.connect(self.on_NewSample)
            self.threadGeneration.start()
            
            self.btnStart.setText("Stop Gen")
            self.OldTime = time.time()
            
        
        else:
            print('Stopped')
            self.threadGeneration.terminate()
            self.threadGeneration = None
            
            self.btnStart.setText("Start Gen and Adq!")
        
    def on_NewSample(self):
        Ts = time.time() - self.OldTime
        self.OldTime = time.time()
        print('Sample time', Ts)


#############################MAIN##############################

if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec_()