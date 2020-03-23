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
        # The dictionary LPFilterConfig is passed to LowPassFilter class as
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
        # To have a complex Vcoi signal, the exponential form of a cosinues
        # is used to calculated de local oscilator signal
        step = 2*np.pi*(Fc/self.Fs)
        # notice that Vcoi amplitude is equal to 1
        self.Vcoi = np.complex128(1*np.exp(1j*(step*np.arange(self.nSamples))))
    
    def LockInExec(self):
        # To move acquired signal to BaseBand it is multiplied with the Vcoi
        # to avoid errors in the demodulation process due to phase differences
        # between Vcoi and the acquired signal, real and imaginary parts 
        # are separated
        RealPart = np.real(self.Vcoi*self.ToDemData)
        ImagPart = np.imag(self.Vcoi*self.ToDemData)
        # Low pass filter is applied to filter the high frequency component
        LPF_RealPart = self.LockInLPF.Apply(RealPart)
        LPF_ImagPart = self.LockInLPF.Apply(ImagPart)
        # slice returns an object that can be used to divide strings, arrays..
        sObject = slice(None, None, self.DownFact)
        # Real an Imaginary parts are DownSampled using the Slice Object
        DS_RealPart = LPF_RealPart[sObject]
        DS_ImagPart = LPF_ImagPart[sObject]
        # Finally a Complex array is obtain joining Real and Imaginary Part
        # With a complex array you can see the absolute value (where Phase
        # difference is not appreciated), real and imaginary (where phase
        # difference will cause missmatches) and Angle (where phase difference
        # will cause an angle error between real and imaginary)
        self.complexDem = DS_RealPart + (DS_ImagPart*1j)
        # NewDemodData signal is emit to notice Main that Lock In is ended
        self.NewDemodData.emit()
        # To Demod Data is set to None
        self.ToDemData = None

    def AddData(self, NewData):
        # If data is coming in while the LockIn is still in process, an erro
        # notification is printed
        if self.ToDemData is not None:
            print('Error Demod !!!!')
        # the data is saved in a class variable
        self.ToDemData = NewData
