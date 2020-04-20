# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 15:03:44 2020

@author: javi8
"""

import os
from qtpy import QtWidgets, uic
import matplotlib.pyplot as plt

import Example_Core as SigGen


class MainWindow(QtWidgets.QDialog):
    "Main Window"
    OutFigFormats = ('svg', 'png')
    Generation = None

    def __init__(self, parent=None):
        # "Super" is used to initialize the class from which this class
        # depends, in this case MainWindow depends on Qt.Widget class
        super().__init__()
        QtWidgets.QMainWindow.__init__(self)

        # It takes the .ui file that contains the graphical part of the main
        # program in order to conect the different objects with this script.
        uipath = os.path.join(os.path.dirname(__file__), 'Example_Qt.ui')
        uic.loadUi(uipath, self)

        self.setWindowTitle('Example QtDesigner')

        # Buttons
        '''
        Connect the Button named "StartButton" with the function
        "StartButtonClicked", so when the button is clicked, the code inside
        the function is executed.
        '''
        self.StartButton.clicked.connect(self.StartButtonClicked)

        # # Spin Box Signals (not needed)
        # '''
        # Signals are applied when you want to get the parameters of a spinbox
        # during the execution of the program.
        # '''
        # self.SpnSampRate.valueChanged.connect(self.SamplingRateSignal)

    def StartButtonClicked(self):
        '''
        Executed when the 'start' button is pressed.
        It takes the Signal Setup Configuration variables in order to execute
        the signal generator.
        '''
        print('Start Button Clicked')
        # Calls to a "GetVariables" function to get the different variables of
        # signal configuration
        SigVariables = self.GetVariables()

        # Initialization of Example_Core script
        # Create a Callback in order to generate the signal and execute
        # a function when the signal generated be executed
        self.Generation = SigGen.DataProcess(SigConfig=SigVariables)

        # Define Events
        self.Generation.EventAmDataDone = self.SignalDoneCallback

        # Create Figure
        self.fig, self.ax = plt.subplots()

        # Starts the generation of the signal
        self.Generation.InitSignal()

    def GetVariables(self):
        '''
        Gets the different variables from the QtDesigner Spinboxes or
        ComboBoxes and creates a dictionary for creating the corresponding
        signals.

        Parameters
        ----------
        None

        Returns
        -------
        A Dictionary with the data arranged as follows:
        SigConfig : dictionary
                    {'Fs': 1000.0,
                     'nSamples': 200,
                     'Amplitude': 0.50,
                     'CarrFrequency': 500,
                     'CarrNoise': 0,
                     'Phase': 0,
                     'ModType': Sinusoidal,
                     'ModFrequency': 1000,
                     'ModFactor': 0.10,
                     'ModNoise': 0, }
        '''
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

    def SignalDoneCallback(self, Data, time):
        '''
        Callback function that is executed when data is arranged from
        DataProcessClass from Example_Core script
        '''
        print('SignalDoneCallback')
        self.ax.plot(time, Data)
        self.fig.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()