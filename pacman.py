import pygame as pg
from pacman import Control

pg.init()

game = Control()

game.main_game_loop()
pg.quit()
