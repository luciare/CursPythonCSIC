# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 12:59:47 2020

@author: javier
"""

import pyqtgraph.parametertree.parameterTypes as pTypes
from PyQt5.QtWidgets import QFileDialog
import h5py
from PyQt5 import Qt
import os
import pickle
import numpy as np


SaveFilePars = [{'name': 'Save File',
                 'type': 'action'},
                {'name': 'File Path',
                 'type': 'str',
                 'value': ''},
                {'name': 'MaxSize',
                 'type': 'int',
                 'siPrefix': True,
                 'suffix': 'B',
                 'limits': (1e6, 1e12),
                 'step': 100e6,
                 'value': 50e6}
                ]


###############################################################################
        
# Class responsible to storage the parameters used on the application into a file
class SaveFileParameters(pTypes.GroupParameter):
    def __init__(self, QTparent, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.QTparent = QTparent

        # Add General Configuration Tree 
        self.addChildren(SaveFilePars)

        # Assignment of variables to a functions
        # When a change on the parameter it is done, a signal is send it to 
        # the correspond function in order to apply the necessary changes
        self.param('Save File').sigActivated.connect(self.FileDialog)

    def FileDialog(self):
        '''
        This functions is used to search the directory where the data will 
        be storaged.
        
        Parameters
        ----------
        None

        Returns
        -------
        None.

        '''
        RecordFile, _ = QFileDialog.getSaveFileName(self.QTparent,
                                                    "Recording File",
                                                    "",
                                                    )
        if RecordFile:
            if not RecordFile.endswith('.h5'):
                RecordFile = RecordFile + '.h5'
            self.param('File Path').setValue(RecordFile)

    def FilePath(self):
        '''
        This functions returns the path where the data will be saved.       
        
        Parameters
        ----------
        None

        Returns
        -------
        'File Path'
        
        '''

        return self.param('File Path').value()


###############################################################################

        
# Class responsible to storage the data of the buffer into a .h5 file
class FileBuffer():
    def __init__(self, FileName, MaxSize, nChannels, Fs=None, ChnNames=None):
        
        # init the local variables into a global variables in order to use 
        # them in other functions inside this class
        self.FileBase = FileName.split('.h5')[0]
        self.PartCount = 0
        self.nChannels = nChannels
        self.MaxSize = MaxSize
        self.Fs = Fs
        self.ChnNames = ChnNames
        self._initFile()

    def _initFile(self):
        '''
        This functions sets the parameters necessary to storage the data into a 
        .h5 file like the filename, filesize, etc..
        
        Parameters
        ----------
        None

        Returns
        -------
        None        
        '''

        if self.MaxSize is not None:
            FileName = '{}_{}.h5'.format(self.FileBase, self.PartCount)
        else:
            FileName = self.FileBase + '.h5'
        self.FileName = FileName
        self.PartCount += 1
        self.h5File = h5py.File(FileName, 'w')
        if self.Fs is not None:
            self.FsDset = self.h5File.create_dataset('Fs', 
                                                     data=self.Fs)
        if self.ChnNames is not None:
            self.ChnNamesDset = self.h5File.create_dataset('ChnNames', 
                                                           dtype='S10',
                                                           data=self.ChnNames)
        
        self.Dset = self.h5File.create_dataset('data',
                                               shape=(0, self.nChannels),
                                               maxshape=(None, self.nChannels),
                                               compression="gzip")

    def AddSample(self, Sample):
        '''
        This functions add the newdata into a file       
        
        Parameters
        ----------
        Sample

        Returns
        -------
        None        
        '''
        nSamples = Sample.shape[0]
        FileInd = self.Dset.shape[0]
        self.Dset.resize((FileInd + nSamples, self.nChannels))
        self.Dset[FileInd:, :] = Sample
        self.h5File.flush()

        stat = os.stat(self.FileName)
        if stat.st_size > self.MaxSize:
            self._initFile()


class DataSavingThread(Qt.QThread):
    def __init__(self, FileName, nChannels, Fs=None, ChnNames=None, 
                 MaxSize=None, tWait=10, dtype='float'):
        super(DataSavingThread, self).__init__()
        self.NewData = None
        self.tWait = tWait
        self.FileBuff = FileBuffer(FileName=FileName,
                                   nChannels=nChannels,
                                   MaxSize=MaxSize,
                                   Fs=Fs,
                                   ChnNames=ChnNames)

    def run(self, *args, **kwargs):
        while True:
            if self.NewData is not None:
                self.FileBuff.AddSample(self.NewData)
                self.NewData = None
            else:
                Qt.QThread.msleep(self.tWait)

    def AddData(self, NewData):
        if self.NewData is not None:
            print('Error Saving !!!!')
        self.NewData = NewData
    
    def stop (self):
        self.FileBuff.h5File.close()
        self.terminate()



SaveTreeStatePars = [{'name': 'Save State',
                  'type': 'action'},
                 {'name': 'Load State',
                  'type': 'action'},
                ]

class SaveTreeSateParameters(pTypes.GroupParameter):
    def __init__(self, QTparent, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.QTparent = QTparent
        self.addChildren(SaveTreeStatePars)
        self.param('Save State').sigActivated.connect(self.on_Save)
        self.param('Load State').sigActivated.connect(self.on_Load)

    def _GetParent(self):
        parent = self.parent()

        return parent

    def on_Load(self):
        parent = self._GetParent()        
        
        RecordFile, _ = QFileDialog.getOpenFileName(self.QTparent,
                                                    "state File",
                                                    "",
                                                   )
        
        if RecordFile:
            with open(RecordFile, 'rb') as file:
                parent.restoreState(pickle.loads(file.read()))

    def on_Save(self):
        parent = self._GetParent()        
        
        RecordFile, _ = QFileDialog.getSaveFileName(self.QTparent,
                                                    "state File",
                                                    "",
                                                   )
        
        if RecordFile:
            with open(RecordFile, 'wb') as file:
                file.write(pickle.dumps(parent.saveState()))


