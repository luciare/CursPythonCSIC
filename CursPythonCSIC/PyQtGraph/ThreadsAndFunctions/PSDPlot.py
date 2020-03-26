# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 12:56:42 2020

@author: javier
"""

import pyqtgraph.parametertree.parameterTypes as pTypes
import pyqtgraph as pg
from PyQt5 import Qt
import numpy as np
from scipy.signal import welch


PSDPars = ({'name': 'Fs',
            'type': 'float',
            'value': 1e3,
            'siPrefix': True,
            'suffix': 'Hz'},
           {'name': 'PSDEnable',
            'type': 'bool',
            'value': True},
           {'name': 'Fmin',
            'type': 'float',
            'value': 1,
            'step': 10,
            'siPrefix': True,
            'suffix': 'Hz'},
           {'name': 'nFFT',
            'title': 'nFFT 2**x',
            'type': 'int',
            'value': 15,
            'step': 1},
           {'name': 'scaling',
            'type': 'list',
            'values': ('density', 'spectrum'),
            'value': 'density'},
           {'name': 'nAvg',
            'type': 'int',
            'value': 4,
            'step': 1},
           {'name': 'AcqTime',
            'readonly': True,
            'type': 'float',
            'siPrefix': True,
            'suffix': 's'},
           )

# List of PSD parameters
PSDParsList = ('Fs', 'nFFT', 'nAvg', 'nChannels', 'scaling')

# Dictionary created for determine the style of the label
labelStyle = {'color': '#FFF',
              'font-size': '7pt',
              'bold': True}


###############################################################################

# Class for create the graph
class PgPlotWindow(Qt.QWidget):
    def __init__(self):
        super(PgPlotWindow, self).__init__()
        # Layout creator
        layout = Qt.QVBoxLayout(self) 
        self.pgLayout = pg.GraphicsLayoutWidget()
        self.pgLayout.setFocusPolicy(Qt.Qt.WheelFocus)
        layout.addWidget(self.pgLayout)
        self.setLayout(layout)
        self.setFocusPolicy(Qt.Qt.WheelFocus)
        self.show()


###############################################################################
        
# Class responsible to create a buffer in order to storage the data for plotting
class Buffer2D(np.ndarray):
    def __new__(subtype, Fs, nChannels, ViewBuffer,
                dtype=float, buffer=None, offset=0,
                strides=None, order=None, info=None):
        # Create the ndarray instance of our type, given the usual
        # ndarray input arguments.  This will call the standard
        # ndarray constructor, but return an object of our type.
        # It also triggers a call to InfoArray.__array_finalize__
        BufferSize = int(ViewBuffer*Fs)
        shape = (BufferSize, nChannels)
        obj = super(Buffer2D, subtype).__new__(subtype, shape, dtype,
                                               buffer, offset, strides,
                                               order)
        # set the new 'info' attribute to the value passed
        obj.counter = 0
        obj.totalind = 0
        obj.Fs = float(Fs)
        obj.Ts = 1/obj.Fs
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None:
            return
        self.bufferind = getattr(obj, 'bufferind', None)

    def AddData(self, NewData): 
        '''
        This functions adds the new data and store this data into the buffer
        Parameters
        ----------
        None

        Returns
        -------
        None.

        '''

        newsize = NewData.shape[0]
        self[0:-newsize, :] = self[newsize:, :]
        self[-newsize:, :] = NewData
        self.counter += newsize
        self.totalind += newsize

    def IsFilled(self):
        '''
        This functions gives an event when the buffer is empty and it is ready 
        to do the data calculations
        Paramenters
        ----------
        None

        Returns
        -------
        None.

        '''
        return self.counter >= self.shape[0]

    def GetTimes(self, Size):
        '''
        This functions is used for getting the start time, stop time and 
        sampling time of each event
        Parameters
        ----------
        Size

        Returns
        -------
        times

        '''

        stop = self.Ts * self.totalind
        start = stop - self.Ts*Size
        times = np.arange(start, stop, self.Ts)
        return times[-Size:]

    def Reset(self):
        '''
        This functions is used to reseting the counter of the buffer
        Parameters
        ----------
        None

        Returns
        -------
        None.

        '''
        self.counter = 0


###############################################################################
# Class create for the managing of PSD parameters
class PSDParameters(pTypes.GroupParameter):
    def __init__(self, **kwargs):
        
        pTypes.GroupParameter.__init__(self, **kwargs)

        # Add General Configuration Tree 
        self.addChildren(PSDPars)
        # Assignment of variables to a functions
        # When a change on the parameter it is done, a signal is send it to 
        # the correspond function in order to apply the necessary changes
        self.param('Fs').sigValueChanged.connect(self.on_FsChange)
        self.param('Fmin').sigValueChanged.connect(self.on_FsChange)
        self.param('nFFT').sigValueChanged.connect(self.on_nFFTChange)
        self.param('nAvg').sigValueChanged.connect(self.on_nAvgChange)

    def on_FsChange(self):
        '''
        This functions is used to recalculate PSD parameters when some
        variables are changed. If there are some change on 'Fs' or 'Fmin',
        this function recalculates the nFFT variable and calls to the 
        on_nAvgChange() function.        
        
        Parameters
        ----------
        None

        Returns
        -------
        None.

        '''

        Fs = self.param('Fs').value()
        FMin = self.param('Fmin').value()
        nFFT = np.around(np.log2(Fs/FMin))+1
        self.param('nFFT').setValue(nFFT, blockSignal=self.on_nFFTChange)
        self.on_nAvgChange()

    def on_nFFTChange(self):
        '''
        This functions is used to recalculate PSD parameters when some
        variables are changed. If there are some change on 'nFFT', 
        this function recalculates the Fmin variable and calls to the 
        on_nAvgChange() function.        
        
        Parameters
        ----------
        None

        Returns
        -------
        None.

        '''

        Fs = self.param('Fs').value()
        nFFT = self.param('nFFT').value()
        FMin = Fs/2**nFFT
        self.param('Fmin').setValue(FMin, blockSignal=self.on_FminChange)
        self.on_nAvgChange()

    def on_nAvgChange(self):
        '''
        This functions is used to calculate the necessary time to acquire the
        PSD signal.
        It gets the different defined variables and calculates the time to 
        acquire the signal.        
        
        Parameters
        ----------
        None

        Returns
        -------
        None.

        '''

        Fs = self.param('Fs').value()
        nFFT = self.param('nFFT').value()
        nAvg = self.param('nAvg').value()

        AcqTime = ((2**nFFT)/Fs)*nAvg
        self.param('AcqTime').setValue(AcqTime)

    def GetParams(self):
        '''
        This functions is used to get all the PSD parameters and fill them 
        into a dictionary in order to use each parameter in other functions
        
        Parameters
        ----------
        None

        Returns
        -------
        A Dictionary with the data arranged as follows:
        PSDKwargs : dictionary
                     {'Fs': 1000.0, 
                      'nFFT': 32768, 
                      'nAvg': 4, 
                      'nChannels': 1, 
                      'Scaling': density, }
        '''

        PSDKwargs = {}
        for p in self.children():
            if p.name() not in PSDParsList:
                continue
            PSDKwargs[p.name()] = p.value()
        return PSDKwargs


###############################################################################

class PSDPlotter(Qt.QThread):
    # Init the class for the PSD thread
    def __init__(self, Fs, nFFT, nAvg, nChannels, scaling, ChannelConf):
        # super allows to initialize the classes from which this class depends
        super(PSDPlotter, self).__init__()

        # init the local variables into a global variables in order to use 
        # them in other functions inside this class
        self.scaling = scaling
        self.nFFT = 2**nFFT
        self.nChannels = nChannels
        self.Fs = Fs
        
        self.BufferSize = self.nFFT * nAvg
        self.Buffer = Buffer2D(self.Fs, self.nChannels,
                                self.BufferSize/self.Fs)

        self.Plots = [None]*nChannels
        self.Curves = [None]*nChannels

        # Create plot window where the PSD data will be plotted
        self.wind = PgPlotWindow()
        self.wind.pgLayout.nextRow()
        p = self.wind.pgLayout.addPlot()
        p.setLogMode(True, True)
        p.setLabel('bottom', 'Frequency', units='Hz', **labelStyle)
        if scaling == 'density':
            p.setLabel('left', ' PSD', units=' V**2/Hz', **labelStyle)
        else:
            p.setLabel('left', ' PSD', units=' V**2', **labelStyle)

        for win, chs in ChannelConf.items():
            for ch in chs:
                c = p.plot(pen=pg.mkPen(ch['color'],
                                        width=ch['width']))
                self.Plots[ch['Input']] = p
                self.Curves[ch['Input']] = c

    def run(self, *args, **kwargs):
        '''
        Run function in threads is the loop that will start when thread is
        started.

        Returns
        -------
        None.

        '''

        while True:
            if self.Buffer.IsFilled():
                ff, psd = welch(self.Buffer,
                                fs=self.Fs,
                                nperseg=self.nFFT,
                                scaling=self.scaling,
                                axis=0)
                self.Buffer.Reset()
                for i in range(self.nChannels):
                    self.Curves[i].setData(ff, psd[:, i])
            else:
                Qt.QThread.msleep(10)

    def AddData(self, NewData):
        '''
        Add data function in threads gives the NewData arrival to Buffer in 
        order to manage the Data

        Returns
        -------
        None.

        '''

        self.Buffer.AddData(NewData)

    def stop(self):
        '''
        Stop function in threads is the function responsible for stopping the 
        thread

        Returns
        -------
        None.

        '''

        self.wind.close()
        self.terminate()




