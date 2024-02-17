__author__ = 'marble_xu'

import random
import pygame as pg
import gfx
import constants as c
import bloodbar


class ZombieHead(pg.sprite.Sprite):
    def __init__(self, gm, x, y):
        pg.sprite.Sprite.__init__(self)
        self.name = c.ZOMBIE_HEAD
        self.gm = gm
        self.loadImages()
        self.frame_num = len(self.frames)
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.frame_index = 0
        self.animate_timer = 0
        self.animate_interval = 100
    
    def loadFrames(self, frames, name, image_x, colorkey=c.BLACK):
        frame_list = self.gm.gfx[name]
        rect = frame_list[0].get_rect()
        width, height = rect.w, rect.h
        width -= image_x
        for frame in frame_list:
            frames.append(gfx.get_image(frame, image_x, 0, width, height, colorkey))
            
    def loadImages(self):
        self.frames = []
        self.loadFrames(self.frames, self.name, 0)

    def update(self, current_ticks):
        if current_ticks - self.animate_timer > self.animate_interval:
            self.frame_index += 1
            # 动画播放完毕
            if self.frame_index >= self.frame_num:
                self.kill()
                return
            self.animate_timer = current_ticks
        self.image = self.frames[self.frame_index]

class Zombie(pg.sprite.Sprite):
    def __init__(self, gm, x, y, name, health, head_group=None, damage=1):
        pg.sprite.Sprite.__init__(self)
        self.gm = gm
        self.name = name
        self.frames = []
        self.frame_index = 0
        self.loadImages()
        self.frame_num = len(self.frames)

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        
        self.max_health = health
        self.health = health
        self.damage = damage
        self.dead = False
        self.losHead = False
        self.helmet = False
        self.head_group = head_group

        self.walk_timer = 0
        self.animate_timer = 0
        self.attack_timer = 0
        self.state = c.WALK
        self.animate_interval = 150
        self.ice_slow_ratio = 1
        self.ice_slow_timer = 0
        self.hit_timer = 0
        self.losthead_timer = 0
        self.speed = 2
        self.freeze_timer = 0
        self.is_hypno = False # the zombie is hypo and attack other zombies when it ate a HypnoShroom
        # bloodbar
        self.bloodbar = bloodbar.BloodBar(self.rect.center)
    
    def loadFrames(self, frames, name, image_x, colorkey=c.BLACK):
        frame_list = self.gm.gfx[name]
        rect = frame_list[0].get_rect()
        width, height = rect.w, rect.h
        width -= image_x

        for frame in frame_list:
            frames.append(gfx.get_image(frame, image_x, 0, width, height, colorkey))

    def update(self, current_ticks):
        self.current_time = current_ticks
        self.handleState()
        self.updateIceSlow()
        self.animation()
        self.bloodbar.set_position(self.rect.left, self.rect.bottom)
        self.bloodbar.draw(self.gm.screen, self.health / self.max_health)

    def handleState(self):
        if self.state == c.WALK:
            self.walking()
        elif self.state == c.ATTACK:
            self.attacking()
        elif self.state == c.DIE:
            self.dying()
        elif self.state == c.FREEZE:
            self.freezing()

    def walking(self):
        if self.health <= 0:
            self.setDie()
        elif self.losHead and self.current_time - self.losthead_timer > 400:
            self.setDie()
        elif self.health <= c.LOSTHEAD_HEALTH and not self.losHead:
            self.changeFrames(self.losthead_walk_frames)
            self.setLostHead()
        elif self.health <= c.NORMAL_HEALTH and self.helmet:
            self.changeFrames(self.walk_frames)
            self.helmet = False
            if self.name == c.NEWSPAPER_ZOMBIE:#读报二爷
                self.speed = 4

        if (self.current_time - self.walk_timer) > (c.ZOMBIE_WALK_INTERVAL * self.getTimeRatio()):
            self.walk_timer = self.current_time
            if self.is_hypno:
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed
    
    def attacking(self):
        if self.health <= 0:
            self.setDie()
        elif self.health <= c.LOSTHEAD_HEALTH and not self.losHead:
            self.changeFrames(self.losthead_attack_frames)
            self.setLostHead()
        elif self.health <= c.NORMAL_HEALTH and self.helmet:
            self.changeFrames(self.attack_frames)
            self.helmet = False
        if (self.current_time - self.attack_timer) > (c.ATTACK_INTERVAL * self.getTimeRatio()):
            if self.prey.health > 0:
                if self.prey_is_plant:
                    self.prey.setDamage(self.damage, self)
                else:
                    self.prey.setDamage(self.damage)
            self.attack_timer = self.current_time

        if self.prey.health <= 0:
            self.prey = None
            self.setWalk()
    
    def dying(self):
        pass

    def freezing(self):
        if self.health <= 0:
            self.setDie()
        elif self.health <= c.LOSTHEAD_HEALTH and not self.losHead:
            if self.old_state == c.WALK:
                self.changeFrames(self.losthead_walk_frames)
            else:
                self.changeFrames(self.losthead_attack_frames)
            self.setLostHead()
        if (self.current_time - self.freeze_timer) > c.FREEZE_TIME:
            self.setWalk()

    def setLostHead(self):
        self.losthead_timer = self.current_time
        self.losHead = True
        if self.head_group is not None:
            self.head_group.add(ZombieHead(self.gm, self.rect.centerx, self.rect.bottom))
        self.gm.zombie_manager.zombie_group.remove(self)
        self.gm.zombie_manager.losthead_group.add(self)

    def changeFrames(self, frames):
        '''change image frames and modify rect position'''
        self.frames = frames
        self.frame_num = len(self.frames)
        self.frame_index = 0
        
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx

    def animation(self):
        if self.state == c.FREEZE:
            self.image.set_alpha(192)
            return

        if (self.current_time - self.animate_timer) > (self.animate_interval * self.getTimeRatio()):
            self.frame_index += 1
            # 动画播放完毕
            if self.frame_index >= self.frame_num:
                if self.state == c.DIE:
                    self.kill()
                    return
                self.frame_index = 0
            self.animate_timer = self.current_time

        self.image = self.frames[self.frame_index]
        if self.is_hypno:
            self.image = pg.transform.flip(self.image, True, False)
        if(self.current_time - self.hit_timer) >= 200:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(192)

    def getTimeRatio(self):
        return self.ice_slow_ratio

    def setIceSlow(self):
        '''when get a ice bullet damage, slow the attack or walk speed of the zombie'''
        self.ice_slow_timer = self.current_time
        self.ice_slow_ratio = 2
        self.speed = self.speed /2

    def updateIceSlow(self):
        if self.ice_slow_ratio > 1:
            if (self.current_time - self.ice_slow_timer) > c.ICE_SLOW_TIME:
                self.ice_slow_ratio = 1

    def setDamage(self, damage, ice=False):
        self.health -= damage
        self.hit_timer = self.current_time
        if ice:
            self.setIceSlow()
    
    def setWalk(self):
        self.state = c.WALK
        self.animate_interval = 150
        
        if self.helmet:
            self.changeFrames(self.helmet_walk_frames)
        elif self.losHead:
            self.changeFrames(self.losthead_walk_frames)
        else:
            self.changeFrames(self.walk_frames)

    def setAttack(self, prey, is_plant=True):
        self.prey = prey  # prey can be plant or other zombies
        self.prey_is_plant = is_plant
        self.state = c.ATTACK
        self.attack_timer = self.current_time
        self.animate_interval = 100
        
        if self.helmet:
            self.changeFrames(self.helmet_attack_frames)
        elif self.losHead:
            self.changeFrames(self.losthead_attack_frames)
        else:
            self.changeFrames(self.attack_frames)
    
    def setDie(self):
        self.state = c.DIE
        self.animate_interval = 200
        self.changeFrames(self.die_frames)
    
    def setBoomDie(self):
        self.state = c.DIE
        self.animate_interval = 200
        self.changeFrames(self.boomdie_frames)

    def setFreeze(self, ice_trap_image):
        self.old_state = self.state
        self.state = c.FREEZE
        self.freeze_timer = self.current_time
        self.ice_trap_image = ice_trap_image
        self.ice_trap_rect = ice_trap_image.get_rect()
        self.ice_trap_rect.centerx = self.rect.centerx
        self.ice_trap_rect.bottom = self.rect.bottom

    def drawFreezeTrap(self, surface):
        if self.state == c.FREEZE:
            surface.blit(self.ice_trap_image, self.ice_trap_rect)

    def setHypno(self):
        self.is_hypno = True
        self.setWalk()

class NormalZombie(Zombie):
    def __init__(self, gm, x, y, head_group):
        Zombie.__init__(self, gm, x, y, c.NORMAL_ZOMBIE, c.NORMAL_HEALTH, head_group)

    def loadImages(self):
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        walk_name = self.name
        attack_name = self.name + 'Attack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHeadAttack'
        die_name =  self.name + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]
        
        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name, self.gm.zombie_rects[name]['x'])

        self.frames = self.walk_frames

class ConeHeadZombie(Zombie):
    def __init__(self, gm, x, y, head_group):
        Zombie.__init__(self, gm, x, y, c.CONEHEAD_ZOMBIE, c.CONEHEAD_HEALTH, head_group)
        self.helmet = True

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []
        
        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'
        walk_name = c.NORMAL_ZOMBIE
        attack_name = c.NORMAL_ZOMBIE + 'Attack'
        losthead_walk_name = c.NORMAL_ZOMBIE + 'LostHead'
        losthead_attack_name = c.NORMAL_ZOMBIE + 'LostHeadAttack'
        die_name = c.NORMAL_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]
        
        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name, self.gm.zombie_rects[name]['x'])

        self.frames = self.helmet_walk_frames

class BucketHeadZombie(Zombie):
    def __init__(self, gm, x, y, head_group):
        Zombie.__init__(self, gm, x, y, c.BUCKETHEAD_ZOMBIE, c.BUCKETHEAD_HEALTH, head_group)
        self.helmet = True

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'
        walk_name = c.NORMAL_ZOMBIE
        attack_name = c.NORMAL_ZOMBIE + 'Attack'
        losthead_walk_name = c.NORMAL_ZOMBIE + 'LostHead'
        losthead_attack_name = c.NORMAL_ZOMBIE + 'LostHeadAttack'
        die_name = c.NORMAL_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]
        
        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name, self.gm.zombie_rects[name]['x'])

        self.frames = self.helmet_walk_frames

class FlagZombie(Zombie):
    def __init__(self, gm, x, y, head_group):
        Zombie.__init__(self, gm, x, y, c.FLAG_ZOMBIE, c.FLAG_HEALTH, head_group)
    
    def loadImages(self):
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        walk_name = self.name
        attack_name = self.name + 'Attack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHeadAttack'
        die_name = c.NORMAL_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]
        
        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name, self.gm.zombie_rects[name]['x'])

        self.frames = self.walk_frames

class NewspaperZombie(Zombie):
    def __init__(self, gm, x, y, head_group):
        Zombie.__init__(self, gm, x, y, c.NEWSPAPER_ZOMBIE, c.NEWSPAPER_HEALTH, head_group)
        self.helmet = True

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'
        walk_name = self.name + 'NoPaper'
        attack_name = self.name + 'NoPaperAttack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHeadAttack'
        die_name = self.name + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            if name == c.BOOMDIE:
                color = c.BLACK
            else:
                color = c.WHITE
            self.loadFrames(frame_list[i], name, self.gm.zombie_rects[name]['x'], color)

        self.frames = self.helmet_walk_frames