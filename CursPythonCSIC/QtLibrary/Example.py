# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 15:03:44 2020

@author: javi8
"""

import os
# import sys

# from qtpy.QtWidgets import (QHeaderView, QCheckBox, QSpinBox, QLineEdit,
#                             QDoubleSpinBox, QTextEdit, QComboBox,
#                             QTableWidget, QAction, QMessageBox, QFileDialog,
#                             QInputDialog)

from qtpy import QtWidgets, uic
import Example_Core as SigGen
# from PyQt5.QtWidgets import QApplication
import matplotlib.pyplot as plt
# import numpy as np


class MainWindow(QtWidgets.QDialog):
    OutFigFormats = ('svg', 'png')

    IsRunning = None
    Generation = None

    def __init__(self, parent=None):
        super().__init__()
        QtWidgets.QMainWindow.__init__(self)
        uipath = os.path.join(os.path.dirname(__file__), 'Example_Qt.ui')
        uic.loadUi(uipath, self)
        self.setWindowTitle('Example')

        # Buttons
        '''
        This line connect the Button named "StartButton" with the function
        "StartButtonClicked", so when the button is clicked, the code inside 
        the function is executed.
        '''
        self.StartButton.clicked.connect(self.StartButtonClicked)

        # Spin Box Signals (not needed)
        '''
        This signals are applied when you want get the parameters of a spinbox
        during the execution of the program.
        '''
        self.SpnSampRate.valueChanged.connect(self.GeneralConfiguration)
        self.SpnNSamples.valueChanged.connect(self.GeneralConfiguration)
        self.SpnInterruptTime.valueChanged.connect(self.GeneralConfiguration)
        
        # Combo Box
        # self.CmbCarrierType.currentIndexChanged.connect(self.)
        # self.CmbModType.currentIndexChanged.connect(self.)
        # float(self.CmbCarrierType.currentText())
        
        # self.SignalVariables = [self.SpnSampRate,
        #                         self.SpnNSamples,
        #                         self.SpnInterruptTime,
        #                         self.SpnCarrierFreq,
        #                         self.SpnCarrierPhase,
        #                         self.SpnCarrierAmp,
        #                         self.SpnNoiseLevel,
        #                         self.SpnModFreq,
        #                         self.SpnModFactor,
        #                         self.SpnModNoiseLevel,
        #                         ]


    def StartButtonClicked(self):
        '''
        This function is executed when the 'start' button is pressed. 

        '''
        print('Start Button Clicked')
        if self.IsRunning is None:
            # Get the Signal Configuration Variables
            SigVariables = self.GetVariables()
            # Generation Thread (¿?)
            # Create a Callback in order to generate the signal and execute 
            # a function when the signal generated be executed
            self.Generation = SigGen.DataProcess(SigConfig=SigVariables)

            # Define Events
            self.Generation.EventAmDataDone = self.SignalDoneCallback
            self.IsRunning = True
            self.fig, self.ax = plt.subplots()

            self.StartButton.setText('Stop')
            print('Start Button')
            # self.Generation.Running = True
            self.Generation.InitSignal()
        else:
            print('Stop')
            self.IsRunning = None
            self.StartButton.setText('Start')
            self.Generation.Running = False

    def GetVariables(self):
        SigConfig = {}
        SigConfig['Fs'] = self.SpnSampRate.value()
        SigConfig['nSamples'] = self.SpnNSamples.value()
        SigConfig['Amplitude'] = self.SpnCarrierAmp.value()
        SigConfig['CarrFrequency'] = self.SpnCarrierFreq.value()
        SigConfig['CarrNoise'] = self.SpnNoiseLevel.value()
        SigConfig['Phase'] = self.SpnCarrierPhase.value()
        SigConfig['ModType'] = self.CmbModType.currentText()
        SigConfig['ModFrequency'] = self.SpnModFreq.value()
        SigConfig['ModFactor'] = self.SpnModFactor.value()
        SigConfig['ModNoise'] = self.SpnModNoiseLevel.value()

        return SigConfig

    def GeneralConfiguration(self):
        print('General Configuration')

    def SignalDoneCallback(self, Data, time):
        print('PLot')
        self.ax.plot(Data, time)
        self.fig.canvas.draw()
        

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()