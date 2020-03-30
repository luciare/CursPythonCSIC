# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 14:04:21 2020

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
import Trees.LockInConfiguration as LockInConfig
import ThreadsAndFunctions.LockInThread as LockIn
import Trees.LPFilterConfiguration as LPFilter

import ThreadsAndFunctions.FileModule as FileMod
import ThreadsAndFunctions.TimePlot as TimePlt
import ThreadsAndFunctions.PSDPlot as PSDPlt


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
        self.SaveStateParams = FileMod.SaveTreeSateParameters(QTparent=self,
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
                                                name='Signal SetUp')
        self.Parameters.addChild(self.SigParams)
        # You can create variables of the main class with the values of
        # an specific tree you have created in a concret GroupParameter class
        self.GenParams = self.SigParams.param('GeneralConfig')
        self.CarrParams = self.SigParams.param('CarrierConfig')
        self.ModParams = self.SigParams.param('ModConfig')

# ############################LockInConfig##############################
        # It is added the tree of LockIn_Config to the actual GUI
        self.LockInParams = LockInConfig.LockIn_Config(QTparent=self,
                                                       name='LockIn SetUp')
        # And its parameters are added to Parameters variable
        self.Parameters.addChild(self.LockInParams)
        # A variable with LockInConfig parameters is created
        self.LockInConf = self.LockInParams.param('LockInConfig')
        
# ############################LPFConfig##############################
        # It is added the tree of LPFilterConfig to the actual GUI
        self.LPFParams = LPFilter.LPFilterConfig(QTparent=self,
                                                 name='LPF SetUp')
        # And its parameters are added to Parameters variable
        self.Parameters.addChild(self.LPFParams) 
        # A variable with LPFConfig parameters is created
        self.LPFConf = self.LPFParams.param('LPFConfig')
        
# #############################Plots##############################
        self.PsdPlotParams = PSDPlt.PSDParameters(name='PSD Plot Options')      
        self.PsdPlotParams.param('Fmin').setValue(50)
        self.PsdPlotParams.param('nAvg').setValue(50)
        self.Parameters.addChild(self.PsdPlotParams)

        self.PlotParams = TimePlt.PlotterParameters(name='Plot options')
        self.PlotParams.SetChannels({'Row1': 0,})
        self.Parameters.addChild(self.PlotParams)
        
# ############################Shared Configs##############################  
        # It can be seen that some parameters of different trees are 
        # the same, so they need to have the same value.
        # To force a value in a parameter it is used the statement setValue
        # With the form XX.param('param') you access to a concrete param value
        # With the form self.XX.param.value() you acced to the value of a 
        # SELF variable created in the XX class
        self.LockInConf.param('Fs').setValue(self.SigParams.Fs.value())
        self.LPFConf.param('Fs').setValue(self.SigParams.Fs.value())
        
        self.PlotParams.param('Fs').setValue(self.LockInParams.OutFs.value())
        self.PsdPlotParams.param('Fs').setValue(self.LockInParams.OutFs.value())

        self.LockInConf.param(
                        'CarrFrequency').setValue(
                                         self.SigParams.CarrFreq.value())
        self.LPFConf.param(
                     'CuttOffFreq').setValue(
                                    self.LockInParams.OutFs.value())
        self.LockInConf.param(
                        'nSamples').setValue(
                                    self.SigParams.nSamples.value())

# ############################Instancias for Changes######################
        # Statement sigValueChanged.connect is used to execute a function
        # if the indicated value (param('param')) changes
        # Statement sigTreeStateChanged.connect is used to execute a function
        # if any parameter of the indicated tree changes
        self.CarrParams.param('CarrFrequency').sigValueChanged.connect(self.on_Fc_changed)
        self.GenParams.sigTreeStateChanged.connect(self.on_GenConfig_changed)
        self.CarrParams.sigTreeStateChanged.connect(self.on_CarrierConfig_changed)
        self.ModParams.sigTreeStateChanged.connect(self.on_ModConfig_changed)
        self.LockInConf.param('OutFs').sigValueChanged.connect(self.on_OutFs_changed)
        
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
        self.threadLockIn = None
        self.threadPlotter = None
        self.threadPsdPlotter = None
        self.threadDemodSave = None

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
    def on_Fc_changed(self):
        '''
        This function is used to change the Carrier Frequency value of 
        Lock In tree to the same value specified in Signal Configuration tree

        '''
        self.LockInConf.param(
                        'CarrFrequency').setValue(
                                         self.SigParams.CarrFreq.value())
        if self.threadLockIn is not None:
            self.threadLockIn.LockIn.GenerateVcoiSignal(
                                     self.SigParams.CarrFreq.value())
            
    def on_OutFs_changed(self):
        '''
        This function is used to change the Cutoff Frequency value of 
        Low pass filter tree to the same value specified in Lock In 
        Configuration tree

        '''
        self.LPFConf.param(
                     'CuttOffFreq').setValue(
                                    self.LockInParams.OutFs.value())
                         
        self.PlotParams.param('Fs').setValue(self.LockInParams.OutFs.value())
        self.PsdPlotParams.param('Fs').setValue(self.LockInParams.OutFs.value())

    def on_GenConfig_changed(self):
        '''
        This function is used to change the Sampling frequency value and 
        nSamples value of Lock In and Low pass Filter trees to the ones
        specified in the signal configuration

        '''
        self.LockInConf.param('Fs').setValue(self.SigParams.Fs.value())
        self.LPFConf.param('Fs').setValue(self.SigParams.Fs.value())
        
        self.PlotParams.param('Fs').setValue(self.LockInParams.OutFs.value())
        self.PsdPlotParams.param('Fs').setValue(self.LockInParams.OutFs.value())
        
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
        '''
        This function is used to Generate or destroy the PSD plot

        '''
        if self.threadGeneration is not None:
            self.Gen_Destroy_PsdPlotter()

    def on_PlotEnable_changed(self):
        '''
        This function is used to Generate or destroy the Time plot

        '''
        if self.threadGeneration is not None:
            self.Gen_Destroy_Plotters()

    def on_RefreshTimePlt_changed(self):
        '''
        This function is used to change the refresh time of Time Plot

        '''
        if self.threadPlotter is not None:
            self.threadPlotter.SetRefreshTime(self.PlotParams.param('RefreshTime').value())

    def on_SetViewTimePlt_changed(self):
        '''
        This function is used to change the View time of Time Plot

        '''
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
            # The function Get_LockInConf_Params generates a dictioanry that
            # is saved to pass to other functions as dictionary or kwargs
            self.LockInConfigKwargs = self.LockInParams.Get_LockInConf_Params()
            # The function Get_LPF_Params generates a dictioanry that
            # is saved to pass to other functions as dictionary or kwargs
            self.LPFConfigKwargs = self.LPFParams.Get_LPF_Params()
            # The dictionary is passed to the genration thread
            self.threadGeneration = SigGen.GenerationThread(self.SignalConfigKwargs)
            # As LPF is used in Lock In process, both dictionaries are passed 
            # to the LockIn Thread
            self.threadLockIn = LockIn.LockInThread(self.LockInConfigKwargs, 
                                                    self.LPFConfigKwargs,
                                                    tWait=self.SigParams.tInterrput.value()
                                                    )
            # the Qt signal of the generation thread is connected to a
            # function (on_NewSample) so, when the thread emits this signal
            # the specified function will be executed
            self.threadGeneration.NewGenData.connect(self.on_NewSample)
            self.threadLockIn.NewDemodData.connect(self.on_NewDemodSample)
            # Time and PSD Plots threads are initialized and started
            self.Gen_Destroy_PsdPlotter()
            self.Gen_Destroy_Plotters()
            # Also save thread is initialize and started
            self.SaveFiles()
            # The thread is started, so run function is executed in loop
            self.threadGeneration.start()
            self.threadLockIn.start()

            # Falta iniciar plot y PSD cuando javi los haga para 1

            # Text of the button is changed to 'stop'
            self.btnStart.setText("Stop Gen")
            # The exact time the thread starts is saved
            self.OldTime = time.time()

        else:
            # stopped is printed in the console
            print('Stopped')
            # Thread is terminated and set to None
            self.threadGeneration.NewGenData.disconnect()
            self.threadLockIn.NewDemodData.disconnect()
            self.threadGeneration.terminate()
            self.threadGeneration = None
            self.threadLockIn = None
            if self.threadPlotter is not None:
                self.threadPlotter.stop()
                self.threadPlotter = None

            if self.threadPsdPlotter is not None:
                self.threadPsdPlotter.stop()
                self.threadPsdPlotter = None
            # Also save thread is stopped
            if self.threadDemodSave is not None:
                self.threadDemodSave.stop()
                self.threadDemodSave = None
                
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
        # to read clean signal
        self.threadLockIn.AddData(NewData=self.threadGeneration.OutData)
        # to read noisy signal
        # self.threadLockIn.AddData(NewData=self.threadGeneration.OutNoiseData)

    def on_NewDemodSample(self): 
        print('demodDone')
        if self.threadDemodSave is not None:
            self.threadDemodSave.AddData(self.threadLockIn.OutDemodDataReShape)
            
        if self.threadPlotter is not None:
            self.threadPlotter.AddData(self.threadLockIn.OutDemodDataReShape)

        if self.threadPsdPlotter is not None:
            self.threadPsdPlotter.AddData(self.threadLockIn.OutDemodDataReShape)
# #############################Plots##############################
    def Gen_Destroy_Plotters(self):
        '''
        This function is executed to initialize and start or destroy time plot
        '''
        # If Time plot thread does not exist
        if self.threadPlotter is None:
            # And the plot enable checkbox is selected
            if self.PlotParams.param('PlotEnable').value() is True:
                # A dictionary obtained with Get Params function is saved
                PlotterKwargs = self.PlotParams.GetParams()
                # And is sent to Plotter thread to initialize it
                self.threadPlotter = TimePlt.Plotter(**PlotterKwargs)
                # Then thread is started
                self.threadPlotter.start()
        # If time plot thread exists
        if self.threadPlotter is not None:
            # And plot enable checkbox is not selected
            if self.PlotParams.param('PlotEnable').value() is False:
                # The thread is stopped and set to None
                self.threadPlotter.stop()
                self.threadPlotter = None

    def Gen_Destroy_PsdPlotter(self):
        '''
        This function is executed to initialize and start or destroy PSD plot
        '''
        # If PSD plot thread does not exist
        if self.threadPsdPlotter is None:
            # And the plot enable checkbox is selected
            if self.PsdPlotParams.param('PSDEnable').value() is True:
                # A dictionary obtained with Get Params function is saved
                PlotterKwargs = self.PlotParams.GetParams()
                # And is sent to PSDPlotter thread to initialize it
                self.threadPsdPlotter = PSDPlt.PSDPlotter(ChannelConf=PlotterKwargs['ChannelConf'],
                                                          nChannels=1,
                                                          **self.PsdPlotParams.GetParams())
                # Then thread is started
                self.threadPsdPlotter.start()
        # If PSD plot thread exists
        if self.threadPsdPlotter is not None:
            # And plot enable checkbox is not selected
            if self.PsdPlotParams.param('PSDEnable').value() is False:
                # The thread is stopped and set to None
                self.threadPsdPlotter.stop()
                self.threadPsdPlotter = None

# #############################Saving Files##############################
    def SaveFiles(self):
        '''
        This function is executed to initialize and start save thread
        '''
        # The File Name is obtained from the GUI File Path
        FileName = self.FileParams.param('File Path').value()
        # If the is no file name, No file is printed
        if FileName == '':
            print('No file')
        # If there is file name
        else:
            # It is checked if the file exists, if it exists is removed
            if os.path.isfile(FileName):
                print('Remove File')
                os.remove(FileName)
            # Maximum size alowed for the new file is obtained from the GUI
            MaxSize = self.FileParams.param('MaxSize').value()
            # The threas is initialized
            self.threadDemodSave = FileMod.DataSavingThread(FileName=FileName,
                                                            nChannels=1,
                                                            MaxSize=MaxSize,
                                                            Fs = self.SigParams.Fs.value(),
                                                            tWait=self.SigParams.tInterrput.value(),
                                                            dtype='float')
            # And then started
            self.threadDemodSave.start()
            
# ############################MAIN##############################

if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec_()
