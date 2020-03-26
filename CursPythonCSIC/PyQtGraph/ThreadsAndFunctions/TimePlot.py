# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 12:58:23 2020

@author: javier
"""


import pyqtgraph.parametertree.parameterTypes as pTypes
import pyqtgraph as pg
import copy
from PyQt5 import Qt
import numpy as np
from scipy.signal import welch


ChannelPars = {'name': 'Ch01',
               'type': 'group',
               'children': [{'name': 'name',
                             'type': 'str',
                             'value': 'Ch10'},
                            {'name': 'color',
                             'type': 'color',
                             'value': "FFF"},
                            {'name': 'width',
                             'type': 'float',
                             'value': 0.5},
                            {'name': 'Window',
                             'type': 'int',
                             'value': 1,},
                            {'name': 'Input',
                             'type': 'int',
                             'readonly': True,
                             'value': 1,}]
               }

PlotterPars = ({'name': 'Fs',
                'type': 'float',
                'value': 1e3,
                'siPrefix': True,
                'suffix': 'Hz'},
               {'name': 'PlotEnable',
                'title': 'Plot Enable',
                'type': 'bool',
                'value': True},
               {'name': 'nChannels',
                'readonly': True,
                'type': 'int',
                'value': 1},
                {'name': 'ViewBuffer',
                 'type': 'float',
                 'value': 30,
                 'step': 1,
                 'siPrefix': True,
                 'suffix': 's'},
               {'name': 'ViewTime',
                'type': 'float',
                'value': 10,
                'step': 1,
                'siPrefix': True,
                'suffix': 's'},
               {'name': 'RefreshTime',
                'type': 'float',
                'value': 4,
                'step': 1,
                'siPrefix': True,
                'suffix': 's'},
               {'name': 'Windows',
                'type': 'int',
                'value': 1},
               {'name': 'Channels',
                'type': 'group',
                'children': []},)

# Class create for the managing of Plot parameters
class PlotterParameters(pTypes.GroupParameter):
    def __init__(self, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        # Add General Configuration Tree 
        self.addChildren(PlotterPars)

        # Assignment of variables to a functions
        # When a change on the parameter it is done, a signal is send it to 
        # the correspond function in order to apply the necessary changes
        self.param('Windows').sigValueChanged.connect(self.on_WindowsChange)

    def on_WindowsChange(self):
        '''
        This functions is used to create a number of windows where the signals
        will be ploted. 
        
        It divides the number of channels into the different windows.
        
        Parameters
        ----------
        None

        Returns
        -------
        None.

        '''

        chs = self.param('Channels').children()
        chPWind = int(len(chs)/self.param('Windows').value())
        for ch in chs:
            ind = ch.child('Input').value()
            ch.child('Window').setValue(int(ind/chPWind))

    def SetChannels(self, Channels):
        '''
        This function is used to get control of different parameters of each
        channel like color, index, width line, etc..
        This function get all the channels and assigns to each of them a index 
        number.
        This is usefull to be able to control each channel separately
        Parameters
        ----------
        Channels

        Returns
        -------
        None.

        '''

        self.param('Channels').clearChildren()
        nChannels = len(Channels)
        self.param('nChannels').setValue(nChannels)
        chPWind = int(nChannels/self.param('Windows').value())
        Chs = []
        for chn, ind in Channels.items():
            Ch = copy.deepcopy(ChannelPars)
            pen = pg.mkPen((ind, 1.3*nChannels))
            Ch['name'] = chn
            Ch['children'][0]['value'] = chn
            Ch['children'][1]['value'] = pen.color()
            Ch['children'][3]['value'] = int(ind/chPWind)
            Ch['children'][4]['value'] = ind
            Chs.append(Ch)

        self.param('Channels').addChildren(Chs)

    def GetParams(self):
        '''
        This functions is used to get all the Plot parameters and fill them 
        into a dictionary in order to use each parameter in other functions
        
        Parameters
        ----------
        None

        Returns
        -------
        A Dictionary with the data arranged as follows:
        PlotterKwargs : dictionary
                       {'Fs': 1000.0, 
                        'nChannels': 1, 
                        'ViewBuffer': 30,
                        'ViewTime': 10, 
                        'RefreshTime': 4,
                        'ChannelConf: {'name': 'Ch01',
                                       'color': 'FFF',
                                       'width': '0.5',
                                       'Window': '1',
                                       'Input': '1',}}

        '''

        PlotterKwargs = {}
        for p in self.children():
            if p.name() in ('Channels', 'Windows', 'PlotEnable'):
                continue
            PlotterKwargs[p.name()] = p.value()

        ChannelConf = {}
        for i in range(self.param('Windows').value()):
            ChannelConf[i] = []

        for p in self.param('Channels').children():
            chp = {}
            for pp in p.children():
                chp[pp.name()] = pp.value()
            ChannelConf[chp['Window']].append(chp.copy())

        PlotterKwargs['ChannelConf'] = ChannelConf

        return PlotterKwargs

##############################################################################

# Class for create the graph
class PgPlotWindow(Qt.QWidget):
    def __init__(self):
        super(PgPlotWindow, self).__init__()
        layout = Qt.QVBoxLayout(self) #crea el layout
        self.pgLayout = pg.GraphicsLayoutWidget()
        self.pgLayout.setFocusPolicy(Qt.Qt.WheelFocus)
        layout.addWidget(self.pgLayout)
        self.setLayout(layout) #to install the QVBoxLayout onto the widget
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


##############################################################################


labelStyle = {'color': '#FFF',
              'font-size': '7pt',
              'bold': True}


class Plotter(Qt.QThread):
# Init the class for the PSD thread

    def __init__(self, Fs, nChannels, ViewBuffer, ViewTime, RefreshTime,
                 ChannelConf, ShowTime=True):

        # super allows to initialize the classes from which this class depends
        super(Plotter, self).__init__()

        # init the local variables into a global variables in order to use 
        # them in other functions inside this class
        self.Winds = []
        self.nChannels = nChannels
        self.Plots = [None]*nChannels
        self.Curves = [None]*nChannels

        self.ShowTime = ShowTime
        self.Fs = Fs
        self.Ts = 1/float(self.Fs)
        self.Buffer = Buffer2D(Fs, nChannels, ViewBuffer)
        self.SetRefreshTime(RefreshTime)
        self.SetViewTime(ViewTime)

        # Create plot window where the PSD data will be plotted
        self.Winds = []

        for win, chs in ChannelConf.items():
            wind = PgPlotWindow()
            self.Winds.append(wind)
            xlink = None
            # for ch in chs:
            wind.pgLayout.nextRow()
            p = wind.pgLayout.addPlot()
            p.hideAxis('bottom')
            if chs[0]['name'].endswith('DC'):
                labName = 'DC Channels'
            else:
                labName = 'AC Channels'
            p.setLabel('left',
                       labName,
                       # ch['name'],
                       units='A',
                       **labelStyle)

            p.setDownsampling(auto=True,
                              mode='subsample',
#                                  mode='peak',
                              )
            p.setClipToView(True)
            # c = p.plot(pen=pg.mkPen(ch['color'],
            for ch in chs:

                c = p.plot(pen=pg.mkPen(ch['color'],
                                        width=0.5))
                                    # width=ch['width']))
#                c = p.plot()
                self.Plots[ch['Input']] = p
                self.Curves[ch['Input']] = c

            if xlink is not None:
                p.setXLink(xlink)
            xlink = p
            p.showAxis('bottom')
            if self.ShowTime:
                p.setLabel('bottom', 'Time', units='s', **labelStyle)
            else:
                p.setLabel('bottom', 'Samps', **labelStyle)

    def SetViewTime(self, ViewTime):
        '''
        This functions is used to set the windowtime that the user will see on 
        the graphical part
        
        Parameters
        ----------
        ViewTime

        Returns
        -------
        None.

        '''

        self.ViewTime = ViewTime
        self.ViewInd = int(ViewTime/self.Ts)

    def SetRefreshTime(self, RefreshTime):
        '''
        This functions is used to calculate the necessary time to refreshing
        the plotting part with new data
        
        Parameters
        ----------
        RefreshTime

        Returns
        -------
        None.

        '''

        self.RefreshTime = RefreshTime
        self.RefreshInd = int(RefreshTime/self.Ts)

    def run(self, *args, **kwargs):
        '''
        Run function in threads is the loop that will start when thread is
        started.

        Returns
        -------
        None.

        '''
        while True:
            if self.Buffer.counter > self.RefreshInd:
                if self.ShowTime:
                    t = self.Buffer.GetTimes(self.ViewInd)
                self.Buffer.Reset()
                j = 0
                for i in range(self.nChannels):
                    j += 1e-6
                    if self.ShowTime:
                        self.Curves[i].setData(t, self.Buffer[-self.ViewInd:, i]+float(j))
                        # self.Curves[i].setData(t, self.Buffer[-self.ViewInd:, i])
                    else:
                        # self.Curves[i].setData(self.Buffer[-self.ViewInd:, i]+int(j))
                        self.Curves[i].setData(self.Buffer[-self.ViewInd:, i])
#                    self.Curves[i].setData(NewData[:, i])
#                self.Plots[i].setXRange(self.BufferSize/10,
#                                        self.BufferSize)
            else:
#                pg.QtGui.QApplication.processEvents()
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

        for wind in self.Winds:
            wind.close()
        self.terminate()

