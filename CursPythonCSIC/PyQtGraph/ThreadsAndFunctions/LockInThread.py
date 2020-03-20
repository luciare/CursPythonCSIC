# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 10:48:20 2020

@author: lucia
"""

from PyQt5 import Qt
import numpy as np

import ThreadsAndFunctions.LowPassFilterClass as LockInFilter


class LockInThread(Qt.QThread):
    NewDemodData = Qt.pyqtSignal()

    def __init__(self, LockInConfig, LPFilterConfig):
        # super permits to initialize the classes from which this class depends
        super(LockInThread, self).__init__()
        # The dictionary SigConfig is passed to SignalGenerator class as
        # kwargs, this means you can send the full dictionary and only use
        # the variables in which you are interesed in
        self.LockInLPF = LockInFilter.LowPassFilter(**LPFilterConfig)
        
        # Initiate class variables
        self.Fs = LockInConfig['Fs']
        self.nSamples = LockInConfig['nSamples']
        self.DownFact = LockInConfig['DSFact']
        self.ToDemData = None
        # Calculate Local oscilator carrier signal
        self.GenerateVcoiSignal(LockInConfig['CarrFrequency'])
        
    def run(self):
        '''
        Run function in threads is the loop that will start when thread is
        started.

        Returns
        -------
        None.

        '''
        # while True statement is used to generate a lopp in the run function
        # so, while the thread is active, the while loop is running
        while True:
            # the generation is started
            if self.ToDemData is not None:
                self.LockInExec()

            else:
                Qt.QThread.msleep(10)

    def GenerateVcoiSignal(self, Fc):
        step = 2*np.pi*(Fc/self.Fs)
        self.Vcoi = np.complex128(1*np.exp(1j*(step*np.arange(self.nSamples))))
    
    def LockInExec(self):
        RealPart = np.real(self.Vcoi*self.ToDemData)
        ImagPart = np.imag(self.Vcoi*self.ToDemData)

        LPF_RealPart = self.LockInLPF.Apply(RealPart)
        LPF_ImagPart = self.LockInLPF.Apply(ImagPart)

        sObject = slice(None, None, self.DownFact)

        DS_RealPart = LPF_RealPart[sObject]
        DS_ImagPart = LPF_ImagPart[sObject]

        self.complexDem = DS_RealPart + (DS_ImagPart*1j)

        self.NewDemodData.emit()
        self.ToDemData = None

    def AddData(self, NewData):
        if self.ToDemData is not None:
            print('Error Demod !!!!')
        self.ToDemData = NewData
