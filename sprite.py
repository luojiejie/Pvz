import random
import time
import pygame as pg
import gfx

#STATE
IDLE = 'idle'
FLY = 'fly'
EXPLODE = 'explode'
ATTACK = 'attack'
ATTACKED = 'attacked'
DIGEST = 'digest'
WALK = 'walk'
DIE = 'die'
CRY = 'cry'
FREEZE = 'freeze'
SLEEP = 'sleep'

# 精灵 
class Sprite(pg.sprite.Sprite):
    def __init__(self,name):
        pg.sprite.Sprite.__init__(self)
        self.name = name
        self.image = pg.image.load(name)
        self.rect = self.image.get_rect()

# 背景图
class BGSprite(Sprite):
    def __init__(self, name, top_left):
        super().__init__(name)
        self.rect.topleft = top_left
        
    def update(self):
        pass

# 水平滚动背景图
class HScrollBGSprite(Sprite):
    def __init__(self, name, top_left):
        super().__init__(name)
        self.rect.topleft = top_left
        
    def update(self):
        # self.rect.top += 1
        # if self.rect.top >= 700:
        #     self.rect.top = -700
        self.rect.left += 1
        if self.rect.left >=600:
            self.rect.left = 0

# 植物
class Plant(Sprite):
    def __init__(self,name,center,gm):
        super().__init__(name)
        self.gm = gm
        self.rect.center = center
        self.shoot_speed = 0.3 #发射速度
        self.shoot_time = 0
        self.energy = 0
        
    def update(self):
        key_pressed = pg.key.get_pressed()
        if key_pressed[pg.K_d] and self.rect.right < 1000:
            self.rect.right = self.rect.right + 4
        if key_pressed[pg.K_a] and self.rect.left > 150:
            self.rect.left  =self.rect.left -4
        if key_pressed[pg.K_w] and self.rect.top > 0:
            self.rect.top -= 4
        if key_pressed[pg.K_s] and self.rect.bottom < 570:
            self.rect.bottom += 4
        if key_pressed[pg.K_SPACE]:
            self.shoot()
        
        # print(self.energy)
    
    # 发射
    def shoot(self):
        if time.perf_counter() - self.shoot_time > self.shoot_speed:
            self.real_shoot()  
            self.shoot_time = time.perf_counter()
                
    def real_shoot(self):
        pass
    
    def add_energy(self):
        self.energy += 100
        print(self.energy)
    
    def remove_energy(self, num=1):
        self.energy -= num
        print(self.energy)
            
   
# 豌豆射手
class PeaShooter(Plant):
    def __init__(self,name,center,gm):
        super().__init__(name, center, gm)
    
    # 发射
    def real_shoot(self):
        self.gm.bullet_manager.shoot(self.rect.right, self.rect.top)
    
    def add_energy(self):
        super().add_energy()
        if self.energy > 1000:
            self.gm.plant_manager.switch_repeaterpea(self.rect.center, self.energy)
    
    def remove_energy(self, num):
        super().remove_energy(num)

# 双发豌豆射手
class RepeaterPea(Plant):
    def __init__(self,name,center,gm):
        super().__init__(name, center, gm)
    
    # 发射
    def real_shoot(self):
        # 是否有能量发射冰弹
        if self.energy > 0:
            self.remove_energy(1)
            self.gm.bullet_manager.shoot(self.rect.right, self.rect.top)
            self.gm.bullet_manager.shoot(self.rect.right, self.rect.top+50)
    
    def add_energy(self):
        super().add_energy()
        if self.energy > 2000:
            self.gm.plant_manager.switch_snowpea(self.rect.center, self.energy)
    
    def remove_energy(self, num):
        super().remove_energy(num)
        if self.energy <= 0:
            self.gm.plant_manager.switch_peashooter(self.rect.center, self.energy)
                
# 寒冰射手
class SnowPea(Plant):
    def __init__(self,name,center,gm):
        super().__init__(name, center, gm)
    
    # 发射
    def real_shoot(self):
        # 是否有能量发射冰弹
        if self.energy > 0:
            self.remove_energy(1)
            self.gm.bullet_manager.shoot_icepea(self.rect.right, self.rect.top)
    
    def add_energy(self):
        super().add_energy()
        if self.energy > 3000:
            self.gm.plant_manager.switch_Threepeater(self.rect.center,self.energy)
    
    def remove_energy(self, num):
        super().remove_energy(num)
        if self.energy <= 1000:
            self.gm.plant_manager.switch_repeaterpea(self.rect.center, self.energy)
            
# 三发豌豆射手
class Threepeater(Plant):
    def __init__(self, name, center, gm):
        super().__init__(name, center, gm)
        
     #发射
    def real_shoot(self):
        if self.energy > 0:
            self.remove_energy(1)
            self.gm.bullet_manager.shoot(self.rect.right, self.rect.top-50)
            self.gm.bullet_manager.shoot(self.rect.right, self.rect.top)
            self.gm.bullet_manager.shoot(self.rect.right, self.rect.top+50)
            
    def remove_energy(self, num):
        super().remove_energy(num)
        if self.energy <= 2000:
            self.gm.plant_manager.switch_snowpea(self.rect.center, self.energy)


# 豌豆
class Pea(Sprite):
    def __init__(self,name,x,y):
        super().__init__(name)
        self.rect.left = x
        self.rect.top = y
        self.damage = 2   # 伤害
        self.isIce = False
        
    def update(self):
        self.rect.right += 4
        if self.rect.right > 1000:
            self.kill()            #销毁豌豆
                        
# 物品
class PropSprite(Sprite):
    def __init__(self,name,x,y,type):
        super().__init__(name)
        self.rect.left = x
        self.rect.bottom = y
        self.type = type
        self.disappear = 3  # 一段时间后消失
 
    def update(self):
        self.disappear -= 0.016
        if self.disappear <= 0:
            self.kill()
    
# # 僵尸
# class Zombie(Sprite):
#     def __init__(self,name,speed,type,gm):
#         super().__init__(self, name)
#         self.rect.left = 1000
#         self.rect.bottom = random.randint(100,600 - self.rect.height)
#         self.speed = speed
#         self.type = type
#         self.gm = gm
#         self.hp = 100   # 血量

#     def update(self):
#         self.rect.left -= self.speed
#         if self.rect.left <= 0:
#             self.kill()
#         if (self.rect.left <= 100):
#             self.gm.game_failed()
          
#     # 被攻击
#     def OnHit(self, damage):
#         self.hp = self.hp - damage
#         if self.hp <= 0:
#             self.kill()