# -*- coding: utf-8 -*-
"""
Created on Sat Jun 10 21:21:30 2023

@author: puvlh
"""


from PyQt5.QtWidgets import QMainWindow, QApplication, QProgressBar, QWidget, QVBoxLayout, QLabel
from PyQt5 import QtCore

import sys, time

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


import os
from os import getcwd, listdir
from os.path import splitext, split, abspath,join
import shutil

import requests


class EditorUpdater(QMainWindow):
    def __init__(self,updater):
        super().__init__()

        self.setWindowTitle("Object Creator Updater")
        self.setFixedSize(400, 100)
        
        
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.addStretch()
        
        central_widget.setLayout(layout)
        
        self.label = QLabel('Updating Object Creator')
        layout.addWidget(self.label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 99)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        self.updater = updater

        updater.progressChanged.connect(self.progress_bar.setValue)
        updater.labelChanged.connect(self.label.setText)
        
        self.show()
        
class Updater(QtCore.QThread):
    progressChanged = QtCore.pyqtSignal(int)
    labelChanged = QtCore.pyqtSignal(str)
  
    def __init__(self, app_data_path):
        super().__init__()
        self.cache = join(app_data_path, 'cache')
        if os.path.exists(self.cache):
            shutil.rmtree(self.cache)
        os.makedirs(self.cache)
    
    def run(self):            
        self.labelChanged.emit('Connecting to Github...')
        try:
            response = requests.get("https://api.github.com/repos/danielmeinert/objectcreator/releases/latest")
        except requests.exceptions.ConnectionError:
            self.labelChanged.emit('No internet connection. Aborting update.')
            return 

        url = response.json()['assets'][0]['browser_download_url']
        
        self.labelChanged.emit('Downloading update installer...')        
        filename = self.download_file(url, self.cache)
        
        self.labelChanged.emit('Installing...')
        time.sleep(2)
        os.execl(filename, f"{filename} /SILENT")
        
        

    def download_file(self, url, folder):
        local_filename = join(folder, url.split('/')[-1])
        
        
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
    
            total_length = int(r.headers.get('content-length'))
            with open(local_filename, 'wb') as f:
                i=0
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk:
                    f.write(chunk)
                    self.progressChanged.emit(int(100*i*8192/total_length))
                    i += 1
        
        self.labelChanged.emit('Download complete.')
        
        return local_filename
        
        
        
        
        
def main():
    # if not QApplication.instance():
    #     app = QApplication(sys.argv)
    # else:
    #     app = QApplication.instance()

    #pyi_splash.close()
    app = QApplication(sys.argv)
    
    app_data_path = join(os.environ['APPDATA'],'Object Creator') 
    if not os.path.exists(app_data_path):
        os.makedirs(app_data_path)
    
    updater = Updater(app_data_path)
    main = EditorUpdater(updater)
        
    updater.start()
    
    
    app.exec_()
    

    return main

if __name__ == '__main__':
    m = main()        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        