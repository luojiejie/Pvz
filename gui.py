import pygame as pg
import constants as c

class CreateGUI():
    def __init__(self, gm):
        self.gm = gm
    
    def update(self, current_ticks):
        self.draw_top_text("上下左右移动", 26, c.WHITE)
    
    def draw_top_text(self, content, size, color):
        pg.font.init()
        font = pg.font.SysFont('kaiti', size)
        text = font.render(content, True, color)
        self.gm.screen.blit(text, (5,5))
    