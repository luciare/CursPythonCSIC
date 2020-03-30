# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 10:48:20 2020

@author: lucia
"""

from PyQt5 import Qt
import numpy as np

import ThreadsAndFunctions.LockInClass as LockInClass


class LockInThread(Qt.QThread):
    NewDemodData = Qt.pyqtSignal()

    def __init__(self, LockInConfig, LPFilterConfig):
        '''
        Initialation of the Thread for LockIn

        Parameters
        ----------
        :param LockInConfig: dictionary, contains all variables related with
                             lock in configuration
        LockInConfig : dictionary
                       {'nSamples': 20000.0,
                        'CarrFrequency': 30000.0,
                        'Fs': 2000000.0,
                        'DSFact': 100,
                        'OutFs': 20000.0,
                        'OutType': 'Abs'
                       }
        :param LPFilterConfig: dictionary, contains all variables related with
                               Low pass filter configuration
        LPFilterConfig : dictionary
                       {'Fs': 2000000.0,
                        'CuttOffFreq': 20000.0,
                        'btype': 'lowpass',
                        'Order': 2
                        }

        Returns
        -------
        None.

        '''
        # super permits to initialize the classes from which this class depends
        super(LockInThread, self).__init__()
        
        self.LockIn = LockInClass.LockIn(LockInConfig, LPFilterConfig)
        self.ToDemData = None

        
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
                self.OutDemodData = self.LockIn.LockInExec(self.ToDemData)
                self.OutDemodDataReShape = np.reshape(self.OutDemodData,
                                             (self.OutDemodData.size, 1)
                                             )
                self.NewDemodData.emit()
                self.ToDemData = None

            else:
                Qt.QThread.msleep(10)
    
    def AddData(self, NewData):
        '''
        This function is used to add data to the lock in process

        Parameters
        ----------
        :param: NewData: Data to demodulate (Array)

        Returns
        -------
        None.

        '''
        # If data is coming in while the LockIn is still in process, an erro
        # notification is printed
        if self.ToDemData is not None:
            print('Error Demod !!!!')
        # the data is saved in a class variable
        self.ToDemData = NewData
