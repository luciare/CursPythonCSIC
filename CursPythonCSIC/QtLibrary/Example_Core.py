# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 15:03:53 2020

@author: javi8
"""
import numpy as np
import signal
from PyQt5 import Qt


def GenAMSignal(Fs, nSamples, Amplitude, CarrFrequency, CarrNoise, 
                 Phase, ModType, ModFrequency, ModFactor, ModNoise):

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

        # Some parameters that are going to be needed in several functions are
        # saved as class variables
        t = np.arange(0, ((1/Fs)*(nSamples)), (1/Fs))
        # The amplitude of the modulated signal is calculated as the ampitude
        # of the carrier multiplied with the modulation factor
        AmpMod = Amplitude*ModFactor
        # Depending on the waveform (sinsuoidal or square) the appropiate
        # function is called to generate the modulation wave
        print(ModType, 'ModType')
        if ModType == 'Sinusoidal':
            # The modulation signal is calculated as a cosinus waveform
            Modulation = AmpMod*np.cos(ModFrequency*2*np.pi*(t))
            # a random noise is added to the signal
            ModulationNoise = Modulation + np.real(np.random.normal(0,
                                                                    ModNoise,
                                                                    Modulation.size
                                                                    )
                                                   )
        if ModType == 'Square':
            # The modulation signal is calculated as a square waveform
            Modulation = AmpMod*signal.square(ModFrequency*2*np.pi*(t))
            # a random noise is added to the signal
            ModulationNoise = Modulation + np.real(np.random.normal(0,
                                                                    ModNoise,
                                                                    Modulation.size
                                                                    )
                                                   )
            
        # The carrier signal is calculated as a cosinus waveform
        Carrier = Amplitude*np.cos(CarrFrequency*2*np.pi*(t)+Phase)
        # a random noise is added to the signal
        CarrierNoise = Carrier + np.real(np.random.normal(0,
                                                          CarrNoise,
                                                          Carrier.size
                                                          )
                                         )

        # Signal is generated as the AM modulation of Carrier and modulation
        # signals calculated before without noise
        AMSignal = (1+Modulation)*Carrier
        # Signal is generated as the AM modulation of Carrier and modulation
        # signals calculated before with noise
        AMSignalNoise = (1+ModulationNoise)*CarrierNoise
        
        return AMSignal
        # return AMSignalNoise

class GenerationEvent():

    EventDataDone = None
    
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
        self.SigConfigKwargs = SigConfig



    def GetAmData(self):
        print(self.SigConfigKwargs)
        self.OutData = GenAMSignal(**self.SigConfigKwargs)
        self.OutDataReShape = np.reshape(self.OutData,
                                         (self.OutData.size, 1)
                                         )
        if self.EventDataDone:
            self.EventDataDone(self.OutDataReShape)
        return


class DataProcess(GenerationEvent):

    EventAmDataDone = None

    def InitSignal(self):
        
        self.EventDataDone = self.DataDoneCallback
        self.GetAmData()

    def DataDoneCallback(self, Data):
        if self.EventAmDataDone:
            self.EventAmDataDone(Data)

   
