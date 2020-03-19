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
        # super permits to initialize the classes from which this class depends
        super(SignalGenerator, self).__init__()
        # Some parameters that are going to be needed in several functions are
        # saved as class variables
        self.Fs = Fs
        self.nSamples = nSamples
        self.t = np.arange(0, ((1/self.Fs)*(self.nSamples)), (1/self.Fs))
        # GenCarrier Function is called
        self.GenCarrier(Amp=Amplitude,
                        Fc=CarrFrequency,
                        phi=Phase,
                        Noise=CarrNoise)
        # Depending on the waveform (sinsuoidal or square) the appropiate
        # function is called to generate the modulation wave
        if ModType == 'sinusoidal':
            self.GenModulationSin(Amp=Amplitude,
                                  ModFact=ModFactor,
                                  Fm=ModFrequency,
                                  Noise=ModNoise)
        if ModType == 'square':
            self.GenModulationSqr(Amp=Amplitude,
                                  ModFact=ModFactor,
                                  Fm=ModFrequency,
                                  Noise=ModNoise)

    def GenModulationSin(self, Amp, ModFact, Fm, Noise):
        # The amplitude of the modulated signal is calculated as the ampitude
        # of the carrier multiplied with the modulation factor
        AmpMod = Amp*ModFact
        # The modulation signal is calculated as a cosinus waveform
        self.Modulation = AmpMod*np.cos(Fm*2*np.pi*(self.t))
        # a random noise is added to the signal
        self.ModulationNoise = self.Modulation + np.real(np.random.normal(0,
                                                                          Noise,
                                                                          self.Modulation.size
                                                                          )
                                                         )
        
    def GenModulationSqr(self, Amp, ModFact, Fm, Noise):
        # The amplitude of the modulated signal is calculated as the ampitude
        # of the carrier multiplied with the modulation factor
        AmpMod = Amp*ModFact
        # The modulation signal is calculated as a square waveform
        self.Modulation = AmpMod*signal.square(Fm*2*np.pi*(self.t))
        # a random noise is added to the signal
        self.ModulationNoise = self.Modulation + np.real(np.random.normal(0,
                                                                          Noise,
                                                                          self.Modulation.size
                                                                          )
                                                         )

    def GenCarrier(self, Amp, Fc, phi, Noise):
        # The carrier signal is calculated as a cosinus waveform
        self.Carrier = Amp*np.cos(Fc*2*np.pi*(self.t))
        # a random noise is added to the signal
        self.CarrierNoise = self.Carrier + np.real(np.random.normal(0,
                                                                    Noise,
                                                                    self.Carrier.size
                                                                    )
                                                   )

    def StartGen(self):
        # Signal is generated as the AM modulation of Carrier and modulation
        # signals calculated before without noise
        self.Signal = (1+self.Modulation)*self.Carrier
        # Signal is generated as the AM modulation of Carrier and modulation
        # signals calculated before with noise
        self.SignalNoise = (1+self.ModulationNoise)*self.CarrierNoise
        # Signal Done is emitted to notice generation thread that there is
        # data ready to be read and processed
        self.SignalDone.emit()
