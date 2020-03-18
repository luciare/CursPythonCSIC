# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:21:20 2020

@author: lucia
"""

import numpy as np
from scipy import signal

from PyQt5 import Qt
from PyQt5.QtCore import QObject

class SignalGenerator(QObject):    
    SignalDone = Qt.pyqtSignal()
    
    def __init__(self, Fs, nSamples, Amplitude, CarrFrequency, CarrNoise, Phase,
                 ModType, ModFrequency, ModFactor, ModNoise, **Kwargs):
        '''
        This class is used to generate Carrier and Modulation Waveform and
        combine them as AM Modulation

        Parameters
        ----------
        :param:Fs: float
        :param:nSamples: int
        :param:Amplitude: float
        :param:CarrFrequency: float
        :param:CarrNoise: float
        :param:Phase: int
        :param:ModType: str
        :param:ModFrequency: float
        :param:ModFactor: float
        :param:ModNoise: float
        :param:**Kwargs: kwargs

        Returns
        -------
        None.

        '''
        
        super(SignalGenerator, self).__init__()
        
        self.Amp = Amplitude
        self.Fs = Fs
        self.nSamples = nSamples
        self.t = np.arange(0, ((1/self.Fs)*(self.nSamples)), (1/self.Fs))
        self.GenCarrier(Fc=CarrFrequency,
                        phi=Phase,
                        Noise=CarrNoise)
        if ModType == 'sinusoidal':
            self.GenModulationSin(ModFact=ModFactor, 
                                  Fm=ModFrequency, 
                                  Noise=ModNoise)
        if ModType == 'square':
            self.GenModulationSqr(ModFact=ModFactor, 
                                  Fm=ModFrequency, 
                                  Noise=ModNoise)
        
    def GenModulationSin(self, ModFact, Fm, Noise):
        AmpMod = self.Amp*ModFact
        self.Modulation =AmpMod*np.cos(Fm*2*np.pi*(self.t))
        self.ModulationNoise = self.Modulation + np.real(np.random.normal(0, 
                                                                        Noise, 
                                                                        self.Modulation.size
                                                                        )
                                                         )
    def GenModulationSqr(self, ModFact, Fm, Noise=0):#Como hacerla cuadrada??
        AmpMod = self.Amp*ModFact
        self.Modulation =AmpMod*signal.square(Fm*2*np.pi*(self.t))
        self.ModulationNoise = self.Modulation + np.real(np.random.normal(0, 
                                                                        Noise, 
                                                                        self.Modulation.size
                                                                        )
                                                         )
    def GenCarrier(self, Fc, phi, Noise):
        self.Carrier = self.Amp*np.cos(Fc*2*np.pi*(self.t))
        self.CarrierNoise = self.Carrier + np.real(np.random.normal(0, 
                                                                  Noise, 
                                                                  self.Carrier.size
                                                                  )
                                                 )
    def StartGen(self):
        self.Signal = (1+self.Modulation)*self.Carrier
        self.SignalNoise = (1+self.ModulationNoise)*self.CarrierNoise
        self.SignalDone.emit()
        
    
        