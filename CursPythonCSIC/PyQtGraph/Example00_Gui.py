# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 15:18:09 2020

@author: lucia
"""

from __future__ import print_function
import os

import numpy as np
import time

from PyQt5 import Qt

from pyqtgraph.parametertree import Parameter, ParameterTree

import Trees.SignalConfiguration as SigConfig
import ThreadsAndFunctions.SignalGeneration as SigGen

import PyqtTools.FileModule as FileMod
import PyqtTools.PlotModule as PltMod

class MainWindow(Qt.QWidget):
    ''' Main Window '''
    def __init__(self):
        # 'Super' is used to initialize the class from which this class
        # depends, in this case MainWindow depends on Qt.Widget class
        super(MainWindow, self).__init__()
    # buscar esto que son cosas de la ventana de la gui
        self.setFocusPolicy(Qt.Qt.WheelFocus)
        layout = Qt.QVBoxLayout(self)
        # Qt.QPushButton is used to generate a button in the GUI
        self.btnStart = Qt.QPushButton("Start Gen and Adq!")
        layout.addWidget(self.btnStart)

# #############################Save##############################
        self.SaveStateParams = FileMod.SaveSateParameters(QTparent=self,
                                                          name='State')
        # With this line, it is initize the group of parameters that are
        # going to be part of the full GUI
        self.Parameters = Parameter.create(name='params',
                                           type='group',
                                           children=(self.SaveStateParams,))
# #############################File##############################
        self.FileParams = FileMod.SaveFileParameters(QTparent=self,
                                                     name='Record File')
        self.Parameters.addChild(self.FileParams)

# ############################SignalConfig##############################
        # QTparent indicades that is going to be added a tree in the actual
        # GUI that has already been created.
        # Name is the name that you want as title of your tree in the GUI
        self.SigParams = SigConfig.SignalConfig(QTparent=self,
                                                name='Signal Configuration')

        # You can create variables of the main class with the values of
        # an specific tree you have create in a concret GrouParameter class
        self.GenParams = self.SigParams.param('GeneralConfig')
        self.CarrParams = self.SigParams.param('CarrierConfig')
        self.ModParams = self.SigParams.param('ModConfig')

# #############################Plots##############################
        self.PsdPlotParams = PltMod.PSDParameters(name='PSD Plot Options')
        self.PsdPlotParams.param('Fs').setValue(self.SigParams.Fs.value())
        self.PsdPlotParams.param('Fmin').setValue(50)
        self.PsdPlotParams.param('nAvg').setValue(50)
        self.Parameters.addChild(self.PsdPlotParams)

        self.PlotParams = PltMod.PlotterParameters(name='Plot options')
        self.PlotParams.SetChannels({'Row1': 0,})
        self.PlotParams.param('Fs').setValue(self.SigParams.Fs.value())

        self.Parameters.addChild(self.PlotParams)
        
# ############################Instancias for Changes######################
        # Statement sigTreeStateChanged.connect is used to execute a function
        # if any parameter of the indicated tree changes
        self.GenParams.sigTreeStateChanged.connect(self.on_GenConfig_changed)
        self.CarrParams.sigTreeStateChanged.connect(self.on_CarrierConfig_changed)
        self.ModParams.sigTreeStateChanged.connect(self.on_ModConfig_changed)
        
        self.PlotParams.param('PlotEnable').sigValueChanged.connect(self.on_PlotEnable_changed)
        self.PlotParams.param('RefreshTime').sigValueChanged.connect(self.on_RefreshTimePlt_changed)
        self.PlotParams.param('ViewTime').sigValueChanged.connect(self.on_SetViewTimePlt_changed)
        self.PsdPlotParams.param('PSDEnable').sigValueChanged.connect(self.on_PSDEnable_changed)

# ############################GuiConfiguration##############################
        # Is the same as before functions but for 'Parameters' variable,
        # which conatins all the trees of all the Gui, so on_Params_changed
        # will be execute for any change in the Gui
        self.Parameters.sigTreeStateChanged.connect(self.on_Params_changed)
    # EXPLICAR ESTO TAMBIEN QUE TIENE QUE VER CON LA GUI
        self.treepar = ParameterTree()
        self.treepar.setParameters(self.Parameters, showTop=False)
        self.treepar.setWindowTitle('pyqtgraph example: Parameter Tree')

        layout.addWidget(self.treepar)

        self.setGeometry(550, 10, 300, 700)
        self.setWindowTitle('MainWindow')
        # It is connected the action of click a button with a function
        self.btnStart.clicked.connect(self.on_btnStart)
        # Threads are startes as None
        self.threadGeneration = None
        self.threadPlotter = None
        self.threadPsdPlotter = None

# ############################Changes Control##############################
    def on_Params_changed(self, param, changes):
        '''
        This function is used to print in the consol the changes that have
        been done.

        '''
        print("tree changes:")
        for param, change, data in changes:
            path = self.Parameters.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
        print('  parameter: %s' % childName)
        print('  change:    %s' % change)
        print('  data:      %s' % str(data))
        print('  ----------')

# ############################Changes Emits##############################
    def on_GenConfig_changed(self):
        '''
        This function is used to change the Sampling frequency value and 
        nSamples value of Lock In and Low pass Filter trees to the ones
        specified in the signal configuration

        '''
        self.LockInConf.param('Fs').setValue(self.SigParams.Fs.value())
        self.LPFConf.param('Fs').setValue(self.SigParams.Fs.value())
        self.PlotParams.param('Fs').setValue(self.SigParams.Fs.value())
        self.PsdPlotParams.param('Fs').setValue(self.SigParams.Fs.value())

        self.LockInConf.param(
                        'nSamples').setValue(
                                    self.SigParams.nSamples.value())
    def on_CarrierConfig_changed(self):
        '''
        This function is used to change the Carrier parameters while the
        program is running

        '''
        # It is checked if the Thread of generation is active
        if self.threadGeneration is not None:
            # Gen Carrier function is called and appropiate parameters are
            # sent to generate the new waveform
            SigGen.GenAMSignal(**self.SigParams.Get_SignalConf_Params())

    def on_ModConfig_changed(self):
        '''
        This function is used to change the Modulation parameters while the
        program is running

        '''
        # It is checked if the Thread of generation is active
        if self.threadGeneration is not None:
            if self.ModParams.param('ModType').value() == 'sinusoidal':
                # GenModulation for a sinusoidal waveform function is called
                # and appropiate parameters are sent to generate the new
                # waveform
                SigGen.GenAMSignal(**self.SigParams.Get_SignalConf_Params())

            if self.ModParams.param('ModType').value() == 'square':
                # GenModulation for an square waveform function is called
                # and appropiate parameters are sent to generate the new
                # waveform
                SigGen.GenAMSignal(**self.SigParams.Get_SignalConf_Params())

    def on_PSDEnable_changed(self):
        if self.threadAqc is not None:
            self.Gen_Destroy_PsdPlotter()

    def on_PlotEnable_changed(self):
        if self.threadAqc is not None:
            self.Gen_Destroy_Plotters()

    def on_RefreshTimePlt_changed(self):
        if self.threadPlotter is not None:
            self.threadPlotter.SetRefreshTime(self.PlotParams.param('RefreshTime').value())

    def on_SetViewTimePlt_changed(self):
        if self.threadPlotter is not None:
            self.threadPlotter.SetViewTime(self.PlotParams.param('ViewTime').value())

# ############################START##############################
    def on_btnStart(self):
        '''
        This function is executed when the 'start' button is pressed. It is
        used to initialize the threads, emit signals and data that are
        necessary durint the execution of the program. Also in this function
        the different threads starts.

        '''
        # It is checked if the thread of generation is running
        if self.threadGeneration is None: # If it is not running
            # A dictionary created by the function Get_SignalConf_Params, with
            # all the parameters and values of Signal configuration class is
            # saved in a class variable. This dictionary can be used as kwargs
            self.SignalConfigKwargs = self.SigParams.Get_SignalConf_Params()
            # The dictionary is passed to the genration thread
            self.threadGeneration = SigGen.GenerationThread(self.SignalConfigKwargs)
            # the Qt signal of the generation thread is connected to a
            # function (on_NewSample) so, when the thread emits this signal
            # the specified function will be executed
            self.threadGeneration.NewGenData.connect(self.on_NewSample)

            self.Gen_Destroy_PsdPlotter()
            self.Gen_Destroy_Plotters()
            self.SaveFiles()
            # The thread is started, so run function is executed in loop
            self.threadGeneration.start()

            # Falta iniciar plot y PSD cuando javi los haga para 1

            # Text of the button is changed to 'stop'
            self.btnStart.setText("Stop Gen")
            # The exact time the thread starts is saved
            self.OldTime = time.time()

        else:
            # stopped is printed in the console
            print('Stopped')
            # Thread is terminated and set to None
            self.threadGeneration.terminate()
            self.threadGeneration = None

            if self.threadPlotter is not None:
                self.threadPlotter.stop()
                self.threadPlotter = None

            if self.threadPsdPlotter is not None:
                self.threadPsdPlotter.stop()
                self.threadPsdPlotter = None

            # Button text is changed again
            self.btnStart.setText("Start Gen and Adq!")

    def on_NewSample(self):
        '''
        This function is executed when a new amount of values of the signal
        generated are ready so they can be read and processed
        '''
        # It is calculated the period of Generation Thread with the actual
        # time and the one saved in the last iteration
        Ts = time.time() - self.OldTime
        # Time is saved again to calculate the next periot of the thread
        self.OldTime = time.time()
        # period is printed in the console
        print('Sample time', Ts)
        # Falta mostrat plot y PSD cuando javi los haga para 1
        if self.threadPlotter is not None:
            self.threadPlotter.AddData(self.threadGeneration.OutDataReShape)

        if self.threadPsdPlotter is not None:
            self.threadPsdPlotter.AddData(self.threadGeneration.OutDataReShape)

    def Gen_Destroy_Plotters(self):
        if self.threadPlotter is None:
            if self.PlotParams.param('PlotEnable').value() is True:
                PlotterKwargs = self.PlotParams.GetParams()
                self.threadPlotter = PltMod.Plotter(**PlotterKwargs)
                self.threadPlotter.start()
        if self.threadPlotter is not None:
            if self.PlotParams.param('PlotEnable').value() is False:
                self.threadPlotter.stop()
                self.threadPlotter = None

    def Gen_Destroy_PsdPlotter(self):
        if self.threadPsdPlotter is None:
            if self.PsdPlotParams.param('PSDEnable').value() is True:
                PlotterKwargs = self.PlotParams.GetParams()
                self.threadPsdPlotter = PltMod.PSDPlotter(ChannelConf=PlotterKwargs['ChannelConf'],
                                                          nChannels=1,
                                                          **self.PsdPlotParams.GetParams())
                self.threadPsdPlotter.start()
        if self.threadPsdPlotter is not None:
            if self.PsdPlotParams.param('PSDEnable').value() is False:
                self.threadPsdPlotter.stop()
                self.threadPsdPlotter = None

# #############################Savind Files##############################
    def SaveFiles(self):
        FileName = self.FileParams.param('File Path').value()
        if FileName == '':
            print('No file')
        else:
            if os.path.isfile(FileName):
                print('Remove File')
                os.remove(FileName)
            MaxSize = self.FileParams.param('MaxSize').value()
            self.threadDemodSave = FileMod.DataSavingThread(FileName=FileName,
                                                            nChannels=1,
                                                            MaxSize=MaxSize,
                                                            Fs = self.SigParams.Fs.value(),
                                                            dtype='float')

            self.threadDemodSave.start()

# ############################MAIN##############################

if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec_()
