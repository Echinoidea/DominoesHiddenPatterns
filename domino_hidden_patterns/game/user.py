from game import Game
from player import Player
from deck import Deck
from snake import Snake
from tile import Tile
from enums.orientations import Orientation
from encoder import Encoder
from computer import Computer

from typing import Tuple

class UserGameText:
    """This class is sloppy but this class is only intended for development use.
    """
    
    def __init__(self):
        self.game = Game()
    
    
    def printRoundInfo(self):
        print("====================ROUND {}====================".format(self.game.roundCounter))
        print("Player 1 --------- {}   |   Player 2 --------- {}".format(self.game.player1.points, self.game.player2.points))
        print("Starting round...")
        print("Player {} goes first\n".format(self.game.turn))
    
    
    def printTurn(self, player: Player):
        print("--------------------\nPlayer {}'s turn\nHand: ".format(self.game.turn), end='')
        player.printHand()
        print("\nSnake:\n--------------------")
        self.game.snake.printSnakeItems()
        print("--------------------\n")
    
    
    def getValidMove(self) -> Tuple[Tile, Orientation]:
        validMove = False
        
        while not validMove:
            userMove = input("Select tile in hand to place and which side of the snake to place it on e.g. [1,3];left\n> ")
            userMove = userMove.split(';')
            userMove = (int(userMove[0][1]), int(userMove[0][3]), userMove[1])
            side = Orientation.LEFT if userMove[2] == "left" else Orientation.RIGHT
            
            # print(userMove)
            userTile = Tile(userMove[0], userMove[1])
            
            if not self.game.snake.canAddTile(userTile):
                print("Cannot add [{}, {}] to either endpoint".format(userMove[0], userMove[1]))
            
            if side is Orientation.LEFT:
                if self.game.snake.canAddTileLeft(userTile):
                    validMove = True
                else:
                    print("Cannot add [{}, {}] to endpoint {}".format(userMove[0], userMove[1], side.__str__()))      
                    continue
            elif side is Orientation.RIGHT:
                if self.game.snake.canAddTileRight(userTile):
                    validMove = True
                else:
                    print("Cannot add [{}, {}] to endpoint {}".format(userMove[0], userMove[1], side.__str__()))
                    continue
        
        return (userTile, side)
    
    
    def inputTurn(self, player: Player):
        
        if self.game.mustSkipTurn(player): 
            print("Deck is empty and Player{0} has no valid moves. Player {0} must skip their turn.".format(player.id))
            self.game.skipTurn()
            return
        elif self.game.mustDraw(player):
            print("Player {} has no playable Tiles in hand. Must draw until there is a valid Tile.".format(player.id))
            if not self.game.deck.isDeckEmpty():
                self.game.drawUntilValidTile(player)
        
        
        validMove = self.getValidMove()
        userTile, side = validMove
        
        self.game.playTile(player, userTile, side)
        # print("Successfully added [{}, {}] to the {}".format(userTile.pip1, userTile.pip2, side))
        
        # Win check
        if self.game.checkRoundWin():
            roundWinner = self.game.getRoundWinner()
            roundWinner.player.points += roundWinner.pointsToGain
            print("This round won by Player {}. Gained {} points.".format(
                roundWinner.player.id, roundWinner.pointsToGain))
            if self.game.checkMatchWin():
                matchWinner = self.game.getMatchWinner()
                print("This match has been won by Player {} with {} points!".format(matchWinner.id, matchWinner.points))
    
    
    def inputTurnComp(self, player: Player, computer: Computer):
        if self.game.mustDraw(player) and not self.game.deck.isDeckEmpty():
            print("Player {} has no playable Tiles in hand. Must draw until there is a valid Tile.".format(player.id))
            self.game.drawUntilValidTile(player)
            
        if self.game.mustSkipTurn(player): 
            print("Deck is empty and Player {0} has no valid moves. Player {0} must skip their turn.".format(player.id))
            return
        
        
        
        # validMove = self.getValidMove()
        userTile, side = computer.getFirstPlayableTile()
        
        self.game.playTile(player, userTile, side)
        # print("Successfully added [{}, {}] to the {}".format(userTile.pip1, userTile.pip2, side))
        
        # Win check
        if self.game.checkRoundWin():
            roundWinner = self.game.getRoundWinner()
            roundWinner.player.points += roundWinner.pointsToGain
            print("This round won by Player {}. Gained {} points.".format(
                roundWinner.player.id, roundWinner.pointsToGain))
            if self.game.checkMatchWin():
                matchWinner = self.game.getMatchWinner()
                print("This match has been won by Player {} with {} points!".format(matchWinner.id, matchWinner.points))
        
        
        



encoder = Encoder()
    
for i in range(10):
    ug = UserGameText()
    
    roundCounter = 0
    
    while not ug.game.checkMatchWin():
        ug.game.startRound()
        ug.printRoundInfo()
        
        computer1 = Computer(ug.game.player1, ug.game)
        computer2 = Computer(ug.game.player2, ug.game)
        
        turnCounter = 0
        
        while not ug.game.checkRoundWin():
            if ug.game.turn == 1:
                encoder.recordTurnStartData(ug.game, turnCounter)
                ug.printTurn(ug.game.player1)
                ug.inputTurnComp(ug.game.player1, computer1)
                encoder.recordTurnEndData(ug.game, turnCounter)
            else:
                encoder.recordTurnStartData(ug.game, turnCounter)
                ug.printTurn(ug.game.player2)
                ug.inputTurnComp(ug.game.player2, computer2)
                encoder.recordTurnEndData(ug.game, turnCounter)
            if ug.game.isTie():
                print("Neither player can draw or place any tiles therefore this round is a tie.")
                break
            ug.game.skipTurn()
            turnCounter += 1
            
        encoder.recordRoundData(ug.game, roundCounter)
        roundCounter += 1
        
    encoder.recordMatchData(ug.game, i)

encoder.saveDfToCSV(encoder.matchDf, 'match.csv')
encoder.saveDfToCSV(encoder.roundDf, 'round.csv')
encoder.saveDfToCSV(encoder.turnStartDf, 'turnStart.csv')
encoder.saveDfToCSV(encoder.turnEndDf, 'turnEnd.csv')