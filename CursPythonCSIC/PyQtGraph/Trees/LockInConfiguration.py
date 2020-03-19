# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 15:01:18 2020

@author: lucia
"""

from PyQt5 import Qt
import pyqtgraph.parametertree.parameterTypes as pTypes

from scipy import signal
import numpy as np

LockInParams = ({'name': 'DemodConfig',
                  'type': 'group',
                  'children': ({'name': 'nSamples',
                                'type': 'float',
                                'value': 20e3,
                                'readonly': True,
                                'siPrefix': True,
                                'suffix': 'Samples'},
                               {'name': 'Fs,
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


class DemodParameters(pTypes.GroupParameter):
    def __init__(self, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.addChild(LockInParams)
        self.LockInConfig = self.param('LockInParams')

        self.nSamples = self.LockInConfig.param('nSamples')
        self.Fs = self.LockInConfig.param('Fs')
        self.DSFact = self.LockInConfig.param('DSFact')
        self.OutFs = self.LockInConfig.param('OutFs')
        self.OutType = self.LockInConfig.param('OutType')

        self.LockInConfig.sigTreeStateChanged.connect(self.on_LockIn_changed)
        
    def on_LockIn_changed(self):
        while self.nSamples.value() % self.DSFact.value() != 0:
            self.DSFact.setValue(self.DSFact.value()+1)
        OutFs = self.Fs.value()/self.DSFact.value()
        self.OutFs.setValue(OutFs)
        
    def Get_LockInConf_Params(self):
        LockInConf = {}
        for LockInParams in self.LockInConfig.children():
            LockInConf[LockInParams.name()] = LockInParams.value()

            return LockInConf
