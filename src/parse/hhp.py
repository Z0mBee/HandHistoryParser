import sys

from analyzer.analyzer import AnalyzerException
from analyzer.txtanalyzer import TxtAnalyzer
from handprinter import HandPrinter


class HandHistoryParser:
    
    def parseHistoryTexts(self, historyTexts, options):
        """Parse list of input histories and return tuple list with hand id and parsed history"""
        
        parseResult = []
        
        for historyText in historyTexts:
            analyzer = TxtAnalyzer(historyText)
            analyzer.analyze()
            
            # Skip if option not fulfilled
            if((options.parseWhenHeroPlays and not analyzer.heroActs)
               or (options.parseWhenPreflopOnly and len(analyzer.flopActions) > 0)
               or (options.parseWhenFlopShown and len(analyzer.flopActions) == 0)
               or (options.parseWhenFlopOnly and (len(analyzer.flopActions) == 0 or len(analyzer.turnActions) > 0))
               or (options.parseWhenTurnShown and len(analyzer.turnActions) == 0)
               or (options.parseWhenRiverShown and len(analyzer.riverActions) == 0)
               ):
              continue
            # Print
            else:
                handprinter = HandPrinter(analyzer, options.ignoreHeroBetSize, options.useSimpleNames)
                parsedHistory = handprinter.printHand()
                parseResult.append((analyzer.handId, parsedHistory))
            
        return parseResult

    def parseHandHistory(self, inputFile, outputFile):
        
        try:
            
            with open(inputFile) as file:
                history = file.read()
                analyzer = TxtAnalyzer(history)
                analyzer.analyze()
            
            handprinter = HandPrinter(analyzer,False,False)
            handprinter.printHandToFile(outputFile)    
            
            print("Parsing successful")
            
        except AnalyzerException as e:
            print("Parsing failed")
            print("Error: ",e) 
    
  
if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print("Invalid arguments -> hhp inputfile outputfile")
    
    inputFile = sys.argv[1]
    outputFile = sys.argv[2]
    hhp = HandHistoryParser()
    hhp.parseHandHistory(inputFile, outputFile)  

class HistoryParserOptions:
    '''
    Options for history parser
    '''

    def __init__(self):
      self.useSimpleNames = False
      self.ignoreHeroBetSize = False
      self.parseWhenHeroPlays = False
      self.parseWhenPreflopOnly = False
      self.parseWhenFlopShown = False
      self.parseWhenFlopOnly = False
      self.parseWhenTurnShown = False
      self.parseWhenRiverShown = False
 



    
    
