# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 14:21:50 2020

@author: lucia
"""

import pyqtgraph.parametertree.parameterTypes as pTypes

GeneralConfiguration = {'name': 'GeneralConfig',
                        'type': 'group',
                        'children': ({'name': 'Fs',
                                      'title': 'Sampling Rate',
                                      'type': 'float',
                                      'value': 2e6,
                                      'siPrefix': True,
                                      'suffix': 'Hz'},
                                     {'name': 'nSamples',
                                      'title': 'Number of Samples',
                                      'type': 'int',
                                      'value': int(20e3),
                                      'readonly': False,
                                      'siPrefix': True,
                                      'suffix': 'Samples'},
                                     {'name': 'tInterrupt',
                                      'title': 'Interruption Time',
                                      'type': 'float',
                                      'readonly': True,
                                      'value': 0.5,
                                      'siPrefix': True,
                                      'suffix': 's'},
                                     )
                        }

CarrierConfiguration = {'name': 'CarrierConfig',
                        'type': 'group',
                        'children': ({'name': 'CarrType',
                                      'title': 'Waveform Type',
                                      'type': 'str',
                                      'value': 'sinusoidal',
                                      'readonly': True},
                                     {'name': 'CarrFrequency',
                                      'title': 'Carrier Frequency',
                                      'type': 'float',
                                      'value': 30e3,
                                      'readonly': False,
                                      'siPrefix': True,
                                      'suffix': 'Hz'},
                                     {'name': 'Phase',
                                      'title': 'Carrier Phase',
                                      'type': 'float',
                                      'value': 0,
                                      'siPrefix': True,
                                      'suffix': 'degree'},
                                     {'name': 'Amplitude',
                                      'title': 'Carrier Amplitude',
                                      'type': 'float',
                                      'value': 0.05,
                                      'siPrefix': True,
                                      'suffix': 'V'},
                                     {'name': 'CarrNoise',
                                      'title': 'Noise Level',
                                      'type': 'float',
                                      'value': 0,
                                      'siPrefix': True,
                                      'suffix': 'V'},
                                     )
                        }

ModulationConfiguration = {'name': 'ModConfig',
                           'type': 'group',
                           'children': ({'name': 'ModType',
                                         'title': 'Waveform Type',
                                         'type': 'list',
                                         'values': ['sinusoidal', 'square'],
                                         'value': 'sinusoidal',
                                         'visible': True},
                                        {'name': 'ModFrequency',
                                         'title': 'Modulation Frequency',
                                         'type': 'float',
                                         'value': 1e3,
                                         'readonly': False,
                                         'siPrefix': True,
                                         'suffix': 'Hz'},
                                        {'name': 'ModFactor',
                                         'title': 'Modulation Factor',
                                         'type': 'float',
                                         'value': 0.01,
                                         'siPrefix': True,
                                         'suffix': 'V'},
                                        {'name': 'ModNoise',
                                         'title': 'Noise Level',
                                         'type': 'float',
                                         'value': 0,
                                         'siPrefix': True,
                                         'suffix': 'V'},
                                        )
                           }

class SignalConfig(pTypes.GroupParameter):
    def __init__(self, **kwargs):

        pTypes.GroupParameter.__init__(self, **kwargs)
        # Add General Configuration Tree 
        self.addChild(GeneralConfiguration)
        # And assign its variables
        self.GeneralConfig = self.param('GeneralConfig')
        self.Fs = self.GeneralConfig.param('Fs')
        self.nSamples = self.GeneralConfig.param('nSamples')
        self.tInterrput = self.GeneralConfig.param('tInterrupt')
        # Link the change of a value of the tree to a function
        # With Fs and nSamples is calculated tInterrpution
        self.GeneralConfig.sigTreeStateChanged.connect(self.on_GeneralConfig_changed)
        # Add Carrier Configuration Tree
        self.addChild(CarrierConfiguration)
        self.CarrierConfig = self.param('CarrierConfig')
        # And assign variables
        self.CarrType = self.CarrierConfig.param('CarrType')
        self.CarrFreq = self.CarrierConfig.param('CarrFrequency')
        self.CarrAmp = self.CarrierConfig.param('Amplitude')
        self.CarrPhase = self.CarrierConfig.param('Phase')
        self.CarrNoise = self.CarrierConfig.param('CarrNoise')
        # Link the change of a Frequency value to a function
        # It is needed Freq and Fs to be Multiples
        self.CarrFreq.sigValueChanged.connect(self.on_CarrFreq_changed)
        # Add Modulation Configuration Tree
        self.addChild(ModulationConfiguration)
        self.ModConfig = self.param('ModConfig')
        # And assign variables
        self.ModType = self.ModConfig.param('ModType')
        self.ModFreq = self.ModConfig.param('ModFrequency')
        self.ModFact = self.ModConfig.param('ModFactor')
        self.ModNoise = self.ModConfig.param('ModNoise')
        # Call the on_XX functions to initialize correctly the variables
        self.on_GeneralConfig_changed()
        self.on_CarrFreq_changed()

    def on_GeneralConfig_changed(self):
        '''
        This functions is used to calculate the interruption time. If the
        processes take more time data will be overwritten and lost.

        Returns
        -------
        None.

        '''
        # value is used to aqcuire the value of the variable
        tInt = self.nSamples.value()/self.Fs.value()
        # setValue is used to change a value of the tree
        self.tInterrput.setValue(tInt)
        self.on_CarrFreq_changed()

    def on_CarrFreq_changed(self):
        '''
        This function is used to ensure that carrier frequency and sampling
        frequency are multiples.

        Returns
        -------
        None.

        '''
        # value is used to aqcuire the value of the variable
        Fc = self.CarrFreq.value()
        factor = round((self.nSamples.value()*Fc)/self.Fs.value())
        FcNew = factor*self.Fs.value()/self.nSamples.value()
        # setValue is used to change a value of the tree
        self.CarrFreq.setValue(FcNew)

    def Get_SignalConf_Params(self):
        '''
        This function returns a dictionary conatining all the information
        related with the configurations set in the different signal trees

        Returns
        -------
        :return: A Dictionary with the data arranged as follows:
        SignalConfig : dictionary
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
                      'ModNoise': 0}
        '''
        SignalConfig = {}
        for GeneralConfig in self.GeneralConfig.children():
            SignalConfig[GeneralConfig.name()] = GeneralConfig.value()

        for CarrierConfig in self.CarrierConfig.children():
            SignalConfig[CarrierConfig.name()] = CarrierConfig.value()

        for ModConfig in self.ModConfig.children():
            SignalConfig[ModConfig.name()] = ModConfig.value()

        return SignalConfig
    