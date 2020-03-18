# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:09:59 2020

@author: lucia
"""

from PyQt5 import Qt
import numpy as np

import ThreadsAndFunctions.SignalGenerationClass as SigGenClass

class GenerationThread(Qt.QThread):
    NewGenData = Qt.pyqtSignal()

    def __init__(self, SigConfig):
        '''
        Initialation of the Thread for Generation

        Parameters
        ----------
        :param SigConfig: dictionary, contains all variables related with
                          signal configuration
        SigConfig : dictionary
                    {'Fs': 2000000.0, 
                     'nSamples': 20000, 
                     'tInterrupt': 0.01, 
                     'CarrType': 'sinusoidal', 
                     'CarrFrequency': 30000.0, 
                     'Phase': 0, 
                     'Amplitude': 0.05, 
                     'CarrNoise': 0, 
                     'ModType': 'sinusoidal', 
                     'ModFrequency': 1000.0, 
                     'ModFactor': 0.1, 
                     'ModNoise': 0
                    }

        Returns
        -------
        None.

        '''
        #super permits to initialize the classes from which this class depends
        super(GenerationThread, self).__init__()
        self.SigGen = SigGenClass.SignalGenerator(**SigConfig)
        self.SigGen.SignalDone.connect(self.NewData)

    def run(self):
        '''
        Run function in threads is the loop that will start when thread is
        started.

        Returns
        -------
        None.

        '''
        
        while True:
            self.SigGen.StartGen()
        
    def NewData(self):
        '''
        This function Emits a signal to notify the data is ready

        Returns
        -------
        None.

        '''
        
        OutData = self.SigGen.Signal
        #When Data is generated an emit is done to notify it to main 
        self.NewGenData.emit()
        
        
        
        