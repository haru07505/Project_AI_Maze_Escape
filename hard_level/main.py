import pygame
import sys
import os, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gameEscape import Game
   
if  __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()  