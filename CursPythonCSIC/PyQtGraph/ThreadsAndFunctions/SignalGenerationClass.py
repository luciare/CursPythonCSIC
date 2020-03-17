# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:21:20 2020

@author: lucia
"""

import numpy as np

class SignalGenerator():
    EveryNEvent = None
    def __init__(self, Fs, nSamples, Amplitude, CarrFrequency, CarrNoise, Phase,
                 ModType, ModFrequency, ModFactor, ModNoise, **Kwargs):
        self.Amp = Amplitude
        self.Fs = Fs
        self.nSamples = nSamples
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
        stepMod = 2*np.pi*(Fm/self.Fs)
        self.Modulation = np.complex128(AmpMod*np.exp
                                        (1j*(stepMod*np.arange(self.nSamples)))
                                        )
        self.ModulationNoise = self.Carrier + np.real(np.random.normal(0, 
                                                                       Noise, 
                                                                       self.Modulation.size
                                                                       )
                                                      )
    # def GenModulationSqr(self, Amp, ModFact, Fm, Noise=0):#Como hacerla cuadrada??
    #     AmpMod = Amp*ModFact
    #     stepMod = 2*np.pi*(Fm/self.Fs)
    #     self.Modulation = np.complex128(AmpMod*np.exp
    #                                     (1j*(stepMod*np.arange(self.nSamples)))
    #                                     )
    #     self.ModulationNoise = self.Carrier + np.real(np.random.normal(0, 
    #                                                                    Noise, 
    #                                                                    self.Signal.size
    #                                                                    )
    #                                                   )
    def GenCarrier(self, Fc, phi, Noise):
        step = 2*np.pi*(Fc/self.Fs)
        self.Carrier = np.complex128(self.Amp*np.exp
                                     (1j*(step*np.arange(self.nSamples))+phi)
                                     )
        self.CarrierNoise = self.Carrier + np.real(np.random.normal(0, 
                                                                  Noise, 
                                                                  self.Carrier.size
                                                                  )
                                                 )
    def StartGen(self):
        self.Signal = (1+self.Modulation)*self.Carrier
        self.SignalNoise = (1+self.ModulationNoise)*self.CarrierNoise
        
    def EveryNCallback(self):
        if self.EveryNEvent:
            print('Emit1')
            self.EveryNEvent(self.Signal)