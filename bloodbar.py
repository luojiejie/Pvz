import pygame as pg


class BloodBar():
    def __init__(self, center):
        self.bloodbar = pg.image.load("resource/image/GUI/bloodbar.png")
        self.bg = pg.image.load("resource/image/GUI/bloodbarbg.png")
        self.rect = self.bloodbar.get_rect()
        self.rect.center = center
        self.percent = 1
        self.width = self.rect.width
        self.height = self.rect.height

    def draw(self, screen, percent):
        self.percent = percent
        rect = self.width*self.percent, self.height, self.width, self.height
        self.bloodbar = pg.transform.chop(self.bloodbar, rect)
        screen.blit(self.bg, self.rect.center)
        screen.blit(self.bloodbar, self.rect.center)
    
    def update(self):
        self.percent -= 0.0001
        if (self.percent < 0):
            self.percent = 0
    
    def set_position(self, x, y):
        self.rect.center = (x,y)