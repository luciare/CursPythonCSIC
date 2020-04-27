# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 13:50:21 2020

@author: lucia
"""

from scipy import signal
import numpy as np

class LowPassFilter():
    def __init__(self, Fs, CuttOffFreq, btype, Order):
        '''
        Initialization of LowPassFilterClass

        Parameters
        ----------
        :param: Fs : float
            Sampling Frequency of the Signal
        :param: CuttOffFreq : float
            Cutoff Frequency of the filter
        :param: btype : str
            The type of filter to be applied (lowpass, bandpass, highpass)
        :param: Order : int
            the order of the filter

        Returns
        -------
        None.

        '''
        # the cutoff frequency is normalized using the sampling frequency
        freqs = np.array(CuttOffFreq/2)/(0.5*Fs)
        # signal.butter function returns the numerator and denominator 
        # polynomials of the IIR filter
        self.b, self.a = signal.butter(Order,
                                       freqs,
                                       btype,
                                       )
        # signal lfilter_zi compute an initial state for the `lfilter` 
        # function that corresponds to the steady state of the step response.
        self.zi = signal.lfilter_zi(self.b,
                                    self.a,
                                    )

    def Apply(self, InSignal):
        '''
        This function generates the local oscilator signal

        Parameters
        ----------
        :param: InSignal: Signal to be filtered (array)

        Returns
        -------
        :return: LPF_Signal: filtered signal (array)

        '''
        # signal.lfilter filters data along one-dimension with an IIR filter
        # it returns the array filtered and final filter delay values, that
        # can be used as initial conditions when filtering a periodic signal
        LPF_Signal, self.zi = signal.lfilter(b=self.b,
                                             a=self.a,
                                             x=InSignal,
                                             axis=0,
                                             zi=self.zi
                                             )

        return LPF_Signal
