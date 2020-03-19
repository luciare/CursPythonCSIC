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

# ############################SignalConfig##############################
        # QTparent indicades that is going to be added a tree in the actual
        # GUI that has already been created.
        # Name is the name that you want as title of your tree in the GUI
        self.SigParams = SigConfig.SignalConfig(QTparent=self,
                                                name='Signal Configuration')
        # With this line, it is initize the group of parameters that are
        # going to be part of the full GUI
        self.Parameters = Parameter.create(name='params',
                                           type='group',
                                           children=(self.SigParams,))
        # You can create variables of the main class with the values of
        # an specific tree you have create in a concret GrouParameter class
        self.CarrParams = self.SigParams.param('CarrierConfig')
        self.ModParams = self.SigParams.param('ModConfig')

# ############################Instancias for Changes######################
        # This different function are used to execute a concrete function if
        # there is any change in any variale of a concrete tree
        self.CarrParams.sigTreeStateChanged.connect(self.on_CarrierConfig_changed)
        self.ModParams.sigTreeStateChanged.connect(self.on_ModConfig_changed)

# ############################GuiConfiguration##############################
        # Is the same has before functions but for 'Parameters' variable,
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
    def on_CarrierConfig_changed(self):
        '''
        This function is used to change the Carrier parameters while the
        program is running

        '''
        # It is checked if the Thread of generation is active
        if self.threadGeneration is not None:
            # Gen Carrier function is called and appropiate parameters are
            # sent to generate the new waveform
            self.threadGeneration.SigGen.GenCarrier(Amp=self.CarrParams.param('Amplitude').value(),
                                                    Fc=self.CarrParams.param('CarrFrequency').value(), 
                                                    phi=self.CarrParams.param('Phase').value(), 
                                                    Noise=self.CarrParams.param('CarrNoise').value()
                                                    )

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
                self.threadGeneration.SigGen.GenModulationSin(Amp=self.CarrParams.param('Amplitude').value(),
                                                              ModFact=self.ModParams.param('ModFactor').value(),
                                                              Fm=self.ModParams.param('ModFrequency').value(), 
                                                              Noise=self.ModParams.param('ModNoise').value()
                                                              )

            if self.ModParams.param('ModType').value() == 'square':
                # GenModulation for an square waveform function is called
                # and appropiate parameters are sent to generate the new
                # waveform
                self.threadGeneration.SigGen.GenModulationSqr(Amp=self.CarrParams.param('Amplitude').value(),
                                                              ModFact=self.ModParams.param('ModFactor').value(), 
                                                              Fm=self.ModParams.param('ModFrequency').value(), 
                                                              Noise=self.ModParams.param('ModNoise').value()
                                                              )
       
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


# ############################MAIN##############################

if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = MainWindow()
    mw.show()
    app.exec_()
