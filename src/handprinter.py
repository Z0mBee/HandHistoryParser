
class HandPrinter:
    '''
    Prints analyzed hands
    '''

    def __init__(self, analyzer, ignoreBetSize, useSimpleNames):
        self.analyzer = analyzer;
        self.ingoreBetSize = ignoreBetSize
        self.useSimpleNames = useSimpleNames
        self._findSimplePlayerNames()
        
    def _getHeaderText(self):
        text = "[table]\n"
        text += "sblind = {0.sb}\n".format(self.analyzer)
        text += "bblind = {0.bb}\n".format(self.analyzer)
        text += "gtype = {0.gameType}\n".format(self.analyzer)
        
        return text
        
    def _getPlayerBalanceText(self):
        text = "balances = "
        for idx, playerBalance in enumerate(self.analyzer.playerBalances):
            if idx != 0:
                text += ", "
            text += self._getPlayerName(playerBalance[0]) + " "+ playerBalance[1] 
        text += "\n"
        return text
    
    def _getActionString(self,actions,hero):
        text = "Actions = "
        raised = False
        possibleActionsUnraised = "FKRA"
        possibeActionsRaised = "FCRA"
        for idx, action in enumerate(actions):
            if idx != 0:
                text += ", "
            
            playerName = self._getPlayerName(action[0])
            #hero action
            if(action[0] == hero and action[1] not in ('S', 'B')):
                if(raised):
                    text += playerName + " can " + possibeActionsRaised + " do " + self._getHeroAction(action[1])
                else:
                    text += playerName + " can " + possibleActionsUnraised + " do " + self._getHeroAction(action[1])
            #non-hero action
            else:
                text += playerName + " "+ action[1]
                 
            if(action[1] == 'A' or action[1].find('R') != -1 or (action[1] == 'B' and action[1] != hero)):
                raised = True
        text += "\n"
        return text
    
    def _getHeroAction(self,action):
        if(self.ingoreBetSize):
            return action[0];
        return action;
    
    def _getPlayerName(self,name):
        if(self.useSimpleNames and name in self.simpleName):
            return self.simpleName[name];
        return name;
    
    def _getPreflopText(self):
        text = "[preflop]\n"
        if(self.analyzer.hero):
            text += "Hand = {0.heroCards[0]}, {0.heroCards[1]}\n".format(self.analyzer)
        else:
            text += "Hand = xx, xx\n"
        text += self._getActionString(self.analyzer.pfActions,self.analyzer.hero)
        return text
    
    def _getFlopText(self):
        text = "[flop]\n"
        text += "Cards = {0.flopCards[0]}, {0.flopCards[1]}, {0.flopCards[2]}\n".format(self.analyzer)
        text += self._getActionString(self.analyzer.flopActions,self.analyzer.hero)
        return text
    
    def _getTurnText(self):
        text = "[turn]\n"
        text += "Card = {0.turnCard}\n".format(self.analyzer)
        text += self._getActionString(self.analyzer.turnActions,self.analyzer.hero)
        return text
    
    def _getRiverText(self):
        text = "[river]\n"
        text += "Card = {0.riverCard}\n".format(self.analyzer)
        text += self._getActionString(self.analyzer.riverActions,self.analyzer.hero)
        return text
        
    def printHandToFile(self, filename):
        output = self.printHand()
        with open(filename,'w') as file:
            file.write(output)
            
    def _findSimplePlayerNames(self):
        self.simpleName ={}
         
        #map player names with simple names       
        for i,player in enumerate(self.analyzer.players):
            if player == self.analyzer.hero:
                self.simpleName[player] = "Hero"
            else:
                self.simpleName[player] = "P" + str(i)
        
    def printHand(self):
        output = self._getHeaderText()
        output += self._getPlayerBalanceText()
        output += "\n"        
        output += self._getPreflopText()
        if(len(self.analyzer.flopActions) > 0):
            output += "\n"
            output += self._getFlopText()
        if(len(self.analyzer.turnActions) > 0):
            output += "\n"
            output += self._getTurnText()
        if(len(self.analyzer.riverActions) > 0):
            output += "\n"
            output += self._getRiverText()
            
        return output
        
        
        
        
