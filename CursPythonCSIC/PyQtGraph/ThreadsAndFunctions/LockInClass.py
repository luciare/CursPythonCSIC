# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 18:52:51 2020

@author: lucia
"""

import numpy as np

import ThreadsAndFunctions.LowPassFilterClass as LockInFilter

class LockIn():
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

    def GenerateVcoiSignal(self, Fc):
        '''
        This function generates the local oscilator signal

        Parameters
        ----------
        :param: Fc: Carrier Frequency (float)

        Returns
        -------
        None.

        '''
        # To have a complex Vcoi signal, the exponential form of a cosinues
        # is used to calculated de local oscilator signal
        step = 2*np.pi*(Fc/self.Fs)
        # notice that Vcoi amplitude is equal to 1
        # The result is saved in the class variable self.Vcoi to permit it 
        # change if carrier frequency changed during execution
        self.Vcoi = np.complex128(1*np.exp(1j*(step*np.arange(self.nSamples))))

    def LockInExec(self, ToDemData):
        '''
        This function is used to execute the lock in, the demodulation process
        used in this case is called product detector and consist in the
        multiplication of AM signal and Vcoi to move AM signal to BandBase
        and apply a low pass filter to eliminate high frequency component

        '''
        # To move acquired signal to BaseBand it is multiplied with the Vcoi
        # to avoid errors in the demodulation process due to phase differences
        # between Vcoi and the acquired signal, real and imaginary parts
        # are separated
        RealPart = np.real(self.Vcoi*ToDemData)
        ImagPart = np.imag(self.Vcoi*ToDemData)
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
        self.ComplexDem = DS_RealPart + (DS_ImagPart*1j)

        return self.ComplexDem
