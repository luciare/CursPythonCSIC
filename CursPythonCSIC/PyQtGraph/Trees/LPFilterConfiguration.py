# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 11:19:10 2020

@author: lucia
"""

import pyqtgraph.parametertree.parameterTypes as pTypes

LPFilterParams = ({'name': 'LPFConfig',
                   'type': 'group',
                   'children': ({'name': 'Fs',
                                 'type': 'float',
                                 'value': 2e6,
                                 'readonly': True,
                                 'siPrefix': True,
                                 'suffix': 'Hz'},
                                {'name': 'CuttOffFreq',
                                 'title': 'Cutt Off Frequency',
                                 'type': 'float',
                                 'readonly': True,
                                 'value': 10e3,
                                 'siPrefix': True,
                                 'suffix': 'Hz'},
                                {'name': 'btype',
                                 'title': 'Output Var Type',
                                 'type': 'str',
                                 'value': 'lowpass',
                                 'readonly': True, },
                                {'name': 'Order',
                                 'title': 'LP Filter Order',
                                 'type': 'int',
                                 'value': 2, },
                                )
                   }
                  )


class LPFilterConfig(pTypes.GroupParameter):
    def __init__(self, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.addChild(LPFilterParams)
        self.LPFConf = self.param('LPFConfig')

        self.Fs = self.LPFConf.param('Fs')
        self.btype = self.LPFConf.param('btype')
        self.Order = self.LPFConf.param('Order')

    def Get_LPF_Params(self):
        LPF = {}
        for LPFParams in self.LPFConf.children():
            LPF[LPFParams.name()] = LPFParams.value()

        return LPF

