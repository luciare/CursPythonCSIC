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
        # Add General Configuration Tree 
        self.addChild(LPFilterParams)
        self.LPFConf = self.param('LPFConfig')
        # And assign its variables
        self.Fs = self.LPFConf.param('Fs')
        self.btype = self.LPFConf.param('btype')
        self.Order = self.LPFConf.param('Order')

    def Get_LPF_Params(self):
        '''
        This function returns a dictionary conatining all the information
        related with the configurations set in the different signal trees

        Returns
        -------
        :return: A Dictionary with the data arranged as follows:
        LPF={'nSamples': 20000.0,
             'CarrFrequency': 30000.0,
             'Fs': 2000000.0,
             'DSFact': 100,
             'OutFs': 20000.0,
             'OutType': 'Abs'
             }
        '''
        LPF = {}
        for LPFParams in self.LPFConf.children():
            LPF[LPFParams.name()] = LPFParams.value()

        return LPF

