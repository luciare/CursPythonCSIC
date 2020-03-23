# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 15:01:18 2020

@author: lucia
"""

import pyqtgraph.parametertree.parameterTypes as pTypes

LockInParams = ({'name': 'LockInConfig',
                 'type': 'group',
                 'children': ({'name': 'nSamples',
                               'type': 'float',
                               'value': 20e3,
                               'readonly': True,
                               'siPrefix': True,
                               'suffix': 'Samples'},
                              {'name': 'CarrFrequency',
                               'title': 'Carrier Frequency',
                               'type': 'float',
                               'value': 30e3,
                               'readonly': True,
                               'siPrefix': True,
                               'suffix': 'Hz'},
                              {'name': 'Fs',
                               'type': 'float',
                               'value': 2e6,
                               'readonly': True,
                               'siPrefix': True,
                               'suffix': 'Hz'},
                              {'name': 'DSFact',
                               'title': 'DownSampling Factor',
                               'type': 'int',
                               'value': 100},
                              {'name': 'OutFs',
                               'title': 'Fs Out',
                               'type': 'float',
                               'readonly': True,
                               'value': 10e3,
                               'siPrefix': True,
                               'suffix': 'Hz'},
                              {'name': 'OutType',
                               'title': 'Output Var Type',
                               'type': 'list',
                               'values': ['Real', 'Imag', 'Angle', 'Abs'],
                               'value': 'Abs'},
                              )
                 }
                )


class LockIn_Config(pTypes.GroupParameter):
    def __init__(self, **kwargs):

        pTypes.GroupParameter.__init__(self, **kwargs)
        # Add General Configuration Tree 
        self.addChild(LockInParams)
        self.LockInConfig = self.param('LockInConfig')
        # And assign its variables
        self.nSamples = self.LockInConfig.param('nSamples')
        self.Fs = self.LockInConfig.param('Fs')
        self.DSFact = self.LockInConfig.param('DSFact')
        self.OutFs = self.LockInConfig.param('OutFs')
        self.OutType = self.LockInConfig.param('OutType')
        # Link the change of a value of the tree to a function
        self.LockInConfig.sigTreeStateChanged.connect(self.on_LockIn_changed)
        # Call the on_XX functions to initialize correctly the variable
        self.on_LockIn_changed()

    def on_LockIn_changed(self):
        '''
        This function is used to ensure that the modulus between the number
        os samples of the array generated and the DSFact is equal to 0, so 
        the Array can be sliced DSFact times without loosing any data
        Alos OutFs is calculated as the division of Fs and DSFact

        Returns
        -------
        None.

        '''
        while self.nSamples.value() % self.DSFact.value() != 0:
            self.DSFact.setValue(self.DSFact.value()+1)
        OutFs = self.Fs.value()/self.DSFact.value()
        self.OutFs.setValue(OutFs)

    def Get_LockInConf_Params(self):
        '''
        This function returns a dictionary conatining all the information
        related with the configurations set in the different signal trees

        Returns
        -------
        :return: A Dictionary with the data arranged as follows:
        LockInConf={'nSamples': 20000.0,
                    'CarrFrequency': 30000.0,
                    'Fs': 2000000.0,
                    'DSFact': 100,
                    'OutFs': 20000.0,
                    'OutType': 'Abs'
                    }
        '''
        LockInConf = {}
        for LockInParams in self.LockInConfig.children():
            LockInConf[LockInParams.name()] = LockInParams.value()

        return LockInConf
