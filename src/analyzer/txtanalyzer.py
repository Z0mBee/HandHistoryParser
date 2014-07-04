import re
from .analyzer import Analyzer
from .analyzer import AnalyzerException

class TxtAnalyzer(Analyzer):
    "Analyzes txt poker hand history"
        
    def _getActionFromSearch(self, searchObj):
        actions = ()
        
        betAmountPos = 4
        raiseAmountPos = 4
        
        if(self.pokerSite == PokerSite.STARS):
            raiseAmountPos = 6
        elif(self.pokerSite == PokerSite.IPOKER):
            betAmountPos = 5
            raiseAmountPos = 5
        
        if(searchObj):
            player = searchObj.group(1)
            player = self._correctPlayerName(player)
            
            action = searchObj.group(2)
            amount = None
            if(action == 'folds' or action == 'Fold'):
                action = 'F'
            elif(action == 'checks' or action == 'Check'):
                action = 'K'
            elif(action == 'calls' or action == 'Call'):
                action = 'C'
            elif(action == 'bets' or action == 'Bet'):
                action = 'R'
                amount = searchObj.group(betAmountPos)
            elif(action == 'raises' or action == 'Raise'):
                action = 'R'
                amount = searchObj.group(raiseAmountPos)
            elif(action == 'is all-In' or action == 'Allin'):
                action = 'A'
            else:
                raise AnalyzerException("Unknown player action found. Action : " + action,self.handId)
            
            if(amount):
                actions = (player,action +" "+amount)
            else:
                actions = (player,action)
        return actions
    
    def _correctPlayerName(self,name):
        "Add quotes if player name contains whitespace or no letters"
        if not re.search(".*[a-zA-Z]+.*",name) or " " in name: 
            name= "\"" + name + "\""
        return name
    
    def _analyzePostflop(self, lines):
        
        flopCard1Pos = 2
        flopCard2Pos = 4
        flopCard3Pos = 5
        turnCardPos = 2
        riverCardPos = 2
        
        if(self.pokerSite == PokerSite.PARTY):
            pfActionRegex = r"(.*) (folds|calls|checks|raises|bets|is all-In)( \[.([0-9\.]*) .+\])?"
            cardRegex = r"\*\* Dealing (Flop|Turn|River) \*\* \[ (..)(, (..), (..))? \]"
        elif(self.pokerSite == PokerSite.POKER888):
            pfActionRegex = r"(.*) (folds|calls|checks|raises|bets)( \[.([0-9\.]*)\])?"
            cardRegex = r"\*\* Dealing (flop|turn|river) \*\* \[ (..)(, (..), (..))? \]"
        elif(self.pokerSite == PokerSite.STARS):
            pfActionRegex = r"(.*): (folds|calls|checks|raises|bets)( .([0-9\.]*))?( to .([0-9\.]*))?"
            cardRegex = r"\*\*\* (FLOP|TURN|RIVER) \*\*\* \[(..) (..) (..)( (..))?\]( \[(..)\])?"
            flopCard1Pos = 2
            flopCard2Pos = 3
            flopCard3Pos = 4
            turnCardPos = 8
            riverCardPos = 8
        elif(self.pokerSite == PokerSite.IPOKER):
            pfActionRegex = r"(.*): (Fold|Call|Bet|Check|Raise|Allin)( \(NF\) )?( Allin )?( .([0-9\.]*))?"   
            cardRegex = r"\*\*\* (FLOP|TURN|RIVER) \*\*\* \[(..)( (..) (..))?\]"
          
        
        for line in lines:
            searchObj = re.search(cardRegex, line)
            if(searchObj):
                if(searchObj.group(1) in ("flop","Flop","FLOP")):
                    self.flopCards.append(self._parseCardFormat(searchObj.group(flopCard1Pos)))
                    self.flopCards.append(self._parseCardFormat(searchObj.group(flopCard2Pos)))
                    self.flopCards.append(self._parseCardFormat(searchObj.group(flopCard3Pos)))
                elif(searchObj.group(1)  in ("turn","Turn","TURN")):
                    self.turnCard = self._parseCardFormat(searchObj.group(turnCardPos))
                elif(searchObj.group(1)  in ("river","River","RIVER")):
                    self.riverCard = self._parseCardFormat(searchObj.group(riverCardPos))
                else:
                    raise AnalyzerException("Unknown postflop value")
                
            searchObj = re.search(pfActionRegex, line)
            if(searchObj):
                if(self.riverCard):
                    self.riverActions.append(self._getActionFromSearch(searchObj))
                elif(self.turnCard):
                    self.turnActions.append(self._getActionFromSearch(searchObj))
                elif(len(self.flopCards) > 0):
                    self.flopActions.append(self._getActionFromSearch(searchObj))
                else:
                    raise AnalyzerException("Analyzing error")

        if(len(self.flopCards) < 3 and len(self.flopActions) > 0):
            raise AnalyzerException("Missing flop cards", self.handId)
        if(not self.turnCard and len(self.turnActions) > 0):
            raise AnalyzerException("Missing turn card", self.handId)
        if(not self.riverCard and len(self.riverActions) > 0):
            raise AnalyzerException("Missing river card", self.handId)
        
    def _parseCardFormat(self,card):
        """ Parse card format"""
        
        # Parse from IPoker card format to normal format
        if(self.pokerSite == PokerSite.IPOKER):
            parsedCard = ""
            parsedCard += card[1]
            parsedCard += card[0].lower()
            return parsedCard
        else:
            return card
    
    
    def _analyzePreflop(self, pfLines):
        
        blindRegex = r"(.*) posts (small|big) blind"
        
        
        if(self.pokerSite == PokerSite.PARTY):
            pfActionRegex = r"(.*) (folds|calls|checks|raises|is all-In)( \[.([0-9\.]*) .+\])?"
            dealtToRegex = r"Dealt to (.*) \[  (..) (..) \]"
        elif(self.pokerSite == PokerSite.POKER888):
            pfActionRegex = r"(.*) (folds|calls|checks|raises)( \[.([0-9\.]*)\])?"
            dealtToRegex = r"Dealt to (.*) \[ (..), (..) \]"
        elif(self.pokerSite == PokerSite.STARS):
            blindRegex = r"(.*): posts (small|big) blind"
            dealtToRegex = r"Dealt to (.*) \[(..) (..)\]"
            pfActionRegex = r"(.*): (folds|calls|checks|raises)( .([0-9\.]*))?( to .([0-9\.]*))?"
        elif(self.pokerSite == PokerSite.IPOKER):
            blindRegex = r"(.*): Post (SB|BB) .*"
            dealtToRegex = r"Dealt to (.*) \[(..) (..)\]"
            pfActionRegex = r"(.*): (Fold|Call|Check|Raise|Allin)( \(NF\) )?( Allin )?( .([0-9\.]*))?"
        

        for line in pfLines:
            searchObj = re.search(blindRegex, line)
            if(searchObj):
                player = searchObj.group(1)
                player = self._correctPlayerName(player)
                if(searchObj.group(2) == "small" or searchObj.group(2) == "SB"):
                    self.pfActions.append((player,"S"))
                else:
                    self.pfActions.append((player,"B"))
                
            searchObj = re.search(dealtToRegex, line)
            if(searchObj):
                self.hero = searchObj.group(1)
                self.heroCards.append(self._parseCardFormat(searchObj.group(2)))
                self.heroCards.append(self._parseCardFormat(searchObj.group(3)))
                
            searchObj = re.search(pfActionRegex, line)
            if(searchObj):
                self.pfActions.append(self._getActionFromSearch(searchObj)) 
    
        if(len(self.pfActions) == 0):
            raise AnalyzerException("Could not find any preflop actions", self.handId)
        
        #find players
        for playerAction in self.pfActions:
            if playerAction[0] not in self.players:
                self.players.append(playerAction[0])
        
    def _analyzeSeats(self, lines):
        
        if(self.pokerSite == PokerSite.PARTY):
            seatRegex = r"Seat [0-9]+: (.*) \( .([0-9\.]*) .+ \)"
        elif(self.pokerSite == PokerSite.POKER888):
            seatRegex = r"Seat [0-9]+: (.*) \( .([0-9\.]*) \)"
        elif(self.pokerSite == PokerSite.STARS):
            seatRegex = r"Seat [0-9]+: (.*) \(.([0-9\.]*) in chips\)"
        elif(self.pokerSite == PokerSite.IPOKER):
            seatRegex = r"Seat [0-9]+: (.*) \(.([0-9\.]*) in chips\)( DEALER)?"
        
        for line in lines:
            searchObj = re.search(seatRegex, line)
            if(searchObj):
                player = searchObj.group(1)
                player = self._correctPlayerName(player)
                
                self.playerBalances.append((player, searchObj.group(2)))
        if(len(self.playerBalances) == 0):
            raise AnalyzerException("Could not find any player balances", self.handId)
        
    def _analyzeHeader(self, lines):
        
        gameIdLine = 0
        blindIdLine = 1
        sbPos = 1
        bbPos = 2
        gameTypePos = 3
        
        if(self.pokerSite == PokerSite.PARTY):
            gameIdRegex = r"Game ([0-9]*) \*\*\*\*\*"
            blindRegex = r".([0-9\.]*)/.([0-9\.]*) .+ (.*) Texas Hold'em"
        elif(self.pokerSite == PokerSite.POKER888):
            gameIdRegex = r"Game ([0-9]*) \*\*\*\*\*"
            blindRegex = r".([0-9\.]*)/.([0-9\.]*) Blinds (.*) Holdem"
        elif(self.pokerSite == PokerSite.STARS):
            gameIdRegex = r"Hand #([0-9]*):"
            blindRegex = r"Hold'em (.*) \(.([0-9\.]*)/.([0-9\.]*).*\)"
            blindIdLine = 0
            sbPos = 2
            bbPos = 3
            gameTypePos = 1
        elif(self.pokerSite == PokerSite.IPOKER):
            gameIdRegex = r"GAME #([0-9]*):"
            blindRegex = r"Hold'em  (.*) .([0-9\.]*)/.([0-9\.]*)"
            blindIdLine = 0
            sbPos = 2
            bbPos = 3
            gameTypePos = 1
        
        searchObj = re.search(gameIdRegex, lines[gameIdLine])
        if(searchObj):
            self.handId = searchObj.group(1)
        else:
            raise AnalyzerException("Cannot find game id. Line: " + lines[gameIdLine])
            
        searchObj = re.search(blindRegex, lines[blindIdLine])
        if(searchObj):
            self.sb = searchObj.group(sbPos)
            self.bb = searchObj.group(bbPos)
            if(searchObj.group(gameTypePos) in ("No Limit", "NL")):
                self.gameType = "NL"
            elif(searchObj.group(gameTypePos) in ("Pot Limit", "PL")):
                self.gameType = "PL"
            elif(searchObj.group(gameTypePos) in ("Fixed Limit", "FL")):
                self.gameType = "FL"
            else:
                raise AnalyzerException("Unknown game type. Type: "+searchObj.group(gameTypePos),self.handId)
        else:
            raise AnalyzerException("Cannot find blinds",self.handId)

        
    def findPokerSite(self):
        self.pokerSite = PokerSite.UNKNOWN
        
        headerLine = self.history.getvalue().splitlines()[0]
        
        if(headerLine.find('888poker') != -1):
            self.pokerSite = PokerSite.POKER888
        elif(headerLine.find('***** Hand History') != -1):
            self.pokerSite = PokerSite.PARTY
        elif(headerLine.find('PokerStars') != -1):
            self.pokerSite = PokerSite.STARS
        elif(headerLine.find('GAME') != -1):
            self.pokerSite = PokerSite.IPOKER
        else:
            raise AnalyzerException('Unknown hand history format. Line: '+ headerLine)
   
    def _removeInactivePlayers(self):
        """ Remove all inactive players without preflop actions """
        activePlayerBalances = []
        for playerBalance in self.playerBalances:
            if(playerBalance[0] in self.players): # Check if name is in players list
                activePlayerBalances.append(playerBalance) 
        self.playerBalances = activePlayerBalances    
        
    def analyze(self):
        "Start analyzing hand history"
        
        self.findPokerSite()

        headerLines = []
        seatLines = []
        preflopLines = []
        postflopLines = []
        
        nrHeaderLines = 3
        seatLineSep = " posts "
        preflopLineSep = ""
        postflopLineSep = ""
        
        if(self.pokerSite == PokerSite.PARTY):
            preflopLineSep = "** Dealing Flop **"           
            postflopLineSep = "Game #"
        elif(self.pokerSite == PokerSite.POKER888):
            preflopLineSep = "** Dealing flop **"
            postflopLineSep = "** Summary **" 
        elif(self.pokerSite == PokerSite.STARS or self.pokerSite == PokerSite.IPOKER):
            preflopLineSep = "*** FLOP ***"
            postflopLineSep = "*** SUMMARY ***"
            seatLineSep = " Post "
            nrHeaderLines = 2
                   

        #read header lines
        for i in range(nrHeaderLines):
            line = self.history.readline()
            if(line in ("","\n")):
                raise AnalyzerException("Missing header line")
            headerLines.append(line)

        #read seat lines
        line = self.history.readline()
        while (line.find(seatLineSep) == -1 and line != "") :
            seatLines.append(line)
            line = self.history.readline()

        #read pf lines
        while (line.find(preflopLineSep) == -1 and line != "") :
            preflopLines.append(line)
            line = self.history.readline()

        #read postflop lines
        while (line.find(postflopLineSep) == -1 and line != "") :
            postflopLines.append(line)
            line = self.history.readline()
               
        
        self._analyzeHeader(headerLines)
        self._analyzeSeats(seatLines)
        self._analyzePreflop(preflopLines)
        if(len(postflopLines) > 0):
            self._analyzePostflop(postflopLines)
        self._removeInactivePlayers()
            

class PokerSite():
    STARS = 1
    POKER888 = 2
    PARTY = 3
    IPOKER = 4
    UNKNOWN = 5

                

            
            
            
            
            
                            

        
