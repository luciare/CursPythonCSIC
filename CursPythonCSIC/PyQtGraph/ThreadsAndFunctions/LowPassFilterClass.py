# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 13:50:21 2020

@author: lucia
"""

from scipy import signal
import numpy as np

class LowPassFilter():
    def __init__(self, Fs, CuttOffFreq, btype, Order, **kwargs):
        freqs = np.array(CuttOffFreq)/(0.5*Fs)
        self.b, self.a = signal.butter(Order,
                                       freqs,
                                       btype,
                                       )
        self.zi = signal.lfilter_zi(self.b,
                                    self.a,
                                    )

    def Apply(self, InSignal):
        LPF_Signal, self.zi = signal.lfilter(b=self.b,
                                             a=self.a,
                                             x=InSignal,
                                             axis=0,
                                             zi=self.zi
                                             )

        return LPF_Signal
