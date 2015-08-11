from _io import StringIO
import codecs
import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from analyzer.analyzer import AnalyzerException
from parse.hhp import HistoryParserOptions
from parse.parserthread import ParserThread
from ui_historyparser import Ui_HistoryParserWindow


class HistoryParserWindow(QMainWindow, Ui_HistoryParserWindow):

    def __init__(self, parent=None):
        super(HistoryParserWindow, self).__init__(parent)
        
        self.setupUi(self)         
        self._connectSignals()      
        self.readSettings()       
        
    def _connectSignals(self):    
      self.connect(self.buttonInputFile,SIGNAL("clicked()"), self.selectInputFile)
      self.connect(self.buttonOutputFile,SIGNAL("clicked()"), self.selectOutputFile)
      self.connect(self.buttonInputFolder,SIGNAL("clicked()"), self.selectInputFolder)
      self.connect(self.buttonOutputFolder,SIGNAL("clicked()"), self.selectOutputFolder)
      self.connect(self.buttonParse,SIGNAL("clicked()"), self.parseHistory)
        
    def closeEvent(self, evnt):    
      self.writeSettings();
        
    def selectInputFile(self):
        dirName = "."
        if(self.lineEditInputFile.text()):
            dirName = os.path.dirname(self.lineEditInputFile.text())
        
        fname = QFileDialog.getOpenFileName(self, "Select file", dirName, "Text files (*.txt)")
        self.lineEditInputFile.setText(fname)    
                
    def selectOutputFile(self):  
        dirName = "."
        if(self.lineEditInputFile.text()):
            dirName = os.path.dirname(self.lineEditInputFile.text())  
        fname = QFileDialog.getSaveFileName(self, "Select file", dirName, "Text files (*.txt)")
        self.lineEditOutputFile.setText(fname)
        
    def selectInputFolder(self):  
        dirName = "."
        if(self.lineEditInputFolder.text()):
            dirName = self.lineEditInputFolder.text()
        dirname = QFileDialog.getExistingDirectory(self,"Select folder",dirName,QFileDialog.ShowDirsOnly);  
        self.lineEditInputFolder.setText(dirname)

    def selectOutputFolder(self):  
        dirName = "."
        if(self.lineEditOutputFolder.text()):
            dirName = self.lineEditOutputFolder.text()  
        dirname = QFileDialog.getExistingDirectory(self,"Select folder",dirName,QFileDialog.ShowDirsOnly);  
        self.lineEditOutputFolder.setText(dirname)
    
    def updateParseButton(self, value):
        self.buttonParse.setEnabled(value)   
        # Show busy cursor 
        if(value):
          QApplication.restoreOverrideCursor()  
        else:
          QApplication.setOverrideCursor(QCursor(Qt.BusyCursor))
        
    def displayError(self, title, message):
      QMessageBox.critical(self, title, message)
      
    def displayWarning(self, title, message):    
      QMessageBox.warning(self.parserWindow, title, message)
            
    def parseHistory(self):  
      inputText = self.textEditHistory.toPlainText()
      inputFile = self.lineEditInputFile.text()
      inputFolder = self.lineEditInputFolder.text()
      outputFile = self.lineEditOutputFile.text()
      outputFolder = self.lineEditOutputFolder.text()
      
      options = HistoryParserOptions()
      options.useSimpleNames = self.checkBoxSimpleNames.isChecked()
      options.ignoreHeroBetSize = self.checkBoxIgnoreBetSize.isChecked()
      options.parseWhenHeroPlays = self.checkBoxHeroPlays.isChecked()
      options.parseWhenPreflopOnly = self.checkBoxPreflopOnly.isChecked()
      options.parseWhenFlopShown = self.checkBoxFlopShown.isChecked()
      options.parseWhenFlopOnly= self.checkBoxFlopOnly.isChecked()
      options.parseWhenTurnShown = self.checkBoxTurnShown.isChecked()
      options.parseWhenRiverShown = self.checkBoxRiverShown.isChecked()
      options.includeSiteName = self.checkBoxSiteName.isChecked()
           
      self.parserThread = ParserThread(inputText, inputFile, inputFolder, outputFile, outputFolder, options)
      self.connect(self.parserThread,SIGNAL("updateParseButton"), self.updateParseButton)
      self.connect(self.parserThread,SIGNAL("displayError"), self.displayError)
      self.connect(self.parserThread,SIGNAL("displayWarning"), self.displayWarning)
      self.parserThread.start()
       

    def writeSettings(self):
      settings = QSettings()
      settings.beginGroup("MainWindow")
      settings.setValue("size", self.size())
      settings.setValue("pos", self.pos())
      settings.endGroup()
      settings.setValue("inputFile", self.lineEditInputFile.text())
      settings.setValue("inputFolder", self.lineEditInputFolder.text())
      settings.setValue("outputFile", self.lineEditOutputFile.text())
      settings.setValue("outputFolder", self.lineEditOutputFolder.text())
      settings.setValue("ignoreBetSize", self.checkBoxIgnoreBetSize.isChecked())
      settings.setValue("simpleNames", self.checkBoxSimpleNames.isChecked())
      settings.setValue("heroPlays", self.checkBoxHeroPlays.isChecked())
      settings.setValue("includeSiteName", self.checkBoxSiteName.isChecked())
      settings.setValue("preflopOnly", self.checkBoxPreflopOnly.isChecked())
      settings.setValue("flopShown", self.checkBoxFlopShown.isChecked())
      settings.setValue("flopOnly", self.checkBoxFlopOnly.isChecked())
      settings.setValue("turnShown", self.checkBoxTurnShown.isChecked())
      settings.setValue("riverShown", self.checkBoxRiverShown.isChecked())
          
 
    def readSettings(self):
      settings = QSettings()
      settings.beginGroup("MainWindow")
      if settings.value("size"):
        self.resize(settings.value("size"))
      if settings.value("pos"):
        self.move(settings.value("pos"))
      settings.endGroup()  
        
      self.lineEditInputFile.setText(settings.value("inputFile"))
      self.lineEditInputFolder.setText(settings.value("inputFolder"))
      self.lineEditOutputFile.setText(settings.value("outputFile"))
      self.lineEditOutputFolder.setText(settings.value("outputFolder"))  
      self.checkBoxIgnoreBetSize.setChecked(True  if settings.value("ignoreBetSize") == "true" else False)  
      self.checkBoxSimpleNames.setChecked(True  if settings.value("simpleNames") == "true" else False)
      self.checkBoxHeroPlays.setChecked(True  if settings.value("heroPlays") == "true" else False)  
      self.checkBoxSiteName.setChecked(True  if settings.value("includeSiteName") == "true" else False) 
      self.checkBoxPreflopOnly.setChecked(True  if settings.value("preflopOnly") == "true" else False)  
      self.checkBoxFlopShown.setChecked(True  if settings.value("flopShown") == "true" else False)  
      self.checkBoxFlopOnly.setChecked(True  if settings.value("flopOnly") == "true" else False)  
      self.checkBoxTurnShown.setChecked(True  if settings.value("turnShown") == "true" else False)  
      self.checkBoxRiverShown.setChecked(True  if settings.value("riverShown") == "true" else False)  
        
  
def startGUI():
    app = QApplication(sys.argv)
    app.setOrganizationName("ZomBee")
    app.setOrganizationDomain("zom.bee")
    app.setApplicationName("Hand History Parser")
    tsw = HistoryParserWindow()
    tsw.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    startGUI()     
      



    
 
 
