from _io import StringIO
import codecs
import os
import socket

from PyQt4.Qt import QMessageBox
from PyQt4.QtCore import QThread, SIGNAL, Qt

from analyzer.analyzer import AnalyzerException
from parse.hhp import HandHistoryParser


class ParserThread(QThread):
    def __init__(self, inputText, inputFile, inputFolder, outputFile, outputFolder, options):
        QThread.__init__(self)
        self.inputText = inputText
        self.inputFile = inputFile
        self.inputFolder = inputFolder
        self.outputFile = outputFile
        self.outputFolder = outputFolder
        self.options = options
        
        
    def writeHistory(self,parsedTexts):
        
        defaultFolder = "parsed"
        if(not self.outputFile and not self.outputFolder):
            if not os.path.exists(defaultFolder):
                    os.makedirs(defaultFolder)
        
        # single parsed text
        if(len(parsedTexts) == 1):
            outputfile = self.outputFile
            if(not outputfile):
                if(self.outputFolder):
                    outputfile =  os.path.join(self.outputFolder, parsedTexts[0][0] + ".txt");
                else:
                    outputfile =  os.path.join(defaultFolder, parsedTexts[0][0] + ".txt");
            
            with codecs.open(outputfile,'w','utf-8') as file:
                file.write(parsedTexts[0][1])
        # multiple parsed texts
        elif(len(parsedTexts) > 0):
            outputfolder = self.outputFolder
            
            if(not outputfolder):
                outputfolder = defaultFolder
                     
            for text in parsedTexts:
                with codecs.open(os.path.join(outputfolder,text[0]+".txt"),'w','utf-8') as file:
                    file.write(text[1])
                   
        else:
            raise ParserException("No parse result") 

    def splitHistoryText(self,historyText):
      """ Remove empty lines and save history texts in list"""      
      texts = []      
      text = ""
              
      for line in StringIO(historyText):
          if(line != "\n" and line != "\r\n"):
              text += line 
          elif((line == "\n" or line == "\r\n") and text != ""):
              texts.append(text)
              text = ""
              
      if(text):
          texts.append(text)
      return texts

    def run(self):
      
      try:       
        self.emit(SIGNAL('updateParseButton'), False)
         
        hhp = HandHistoryParser()
        text = None 
          
        if(self.inputText):
          text = self.inputText        
        elif(self.inputFile):
          with codecs.open(self.inputFile,'r','utf-8') as file:
            text = file.read()
        elif(self.inputFolder):
          pass
        else:
          raise ParserException("Specify input")
            
        if(not text and not self.inputFolder):
          raise ParserException("Input is empty")
                 
        # parse all txt files in folder
        if(self.inputFolder):
          for filename in os.listdir(self.inputFolder):
            if filename.endswith(".txt"):
              try:
                with codecs.open(os.path.join(self.inputFolder,filename),'r','utf-8') as file:
                  text = file.read()
                historyTexts = self.splitHistoryText(text)
                parsedTexts = hhp.parseHistoryTexts(historyTexts, self.options)
                self.writeHistory(parsedTexts)
              except AnalyzerException as e: 
                self.emit(SIGNAL('displayError'), "Parsing Error", "File : {0}. {1}".format(filename,str(e))) 
                
        #parse text
        else:
            historyTexts = self.splitHistoryText(text)
            parsedTexts = hhp.parseHistoryTexts(historyTexts, self.options)
            self.writeHistory(parsedTexts)
               
      except (IOError, OSError) as e:
          self.emit(SIGNAL('displayWarning'), "File Error", str(e))         
      except (ParserException, AnalyzerException) as e:
          self.emit(SIGNAL('displayError'), "Parsing Error", str(e)) 
      finally:
          self.emit(SIGNAL('updateParseButton'), True) 
                
      
        
class ParserException(Exception):
    pass     
  
        
