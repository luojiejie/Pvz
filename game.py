import random
import pygame as pg
import sprite
import audio
import gfx
import zombie
import gui


class Game():
    def __init__(self):
        # 初始化
        pg.init()
        # 建立一个大小为600*600的屏幕（大小根据需求设置）
        self.screen = pg.display.set_mode((1000, 600))
        self.clock = pg.time.Clock()
        self.fps = 60
        self.done = False
        self.clock = pg.time.Clock()
        self.keys = pg.key.get_pressed()
        self.mouse_pos = None
        self.mouse_click = [False, False]  # value:[left mouse click, right mouse click]
        self.current_time = 0.0
        self.countdown = 120*60
            
    def run(self):
        # load gfx
        self.gfx = gfx.init_gfx()
        self.zombie_rects = gfx.loadZombieImageRect()
        self.plant_rects = gfx.loadPlantImageRect()
        # manager
        self.bg_manager = BGManager(self)
        self.plant_manager = PlantManage(self)
        self.prop_manager = PropManager(self)
        self.bullet_manager = BulletManager(self)
        self.zombie_manager = ZombieManager(self)
        # 音效
        self.bgm_player = audio.bgm_player()
        self.audio_player = audio.audio_player()
        self.bgm_player.play_bgm()
        # gui
        self.gui = gui.CreateGUI(self)
        
        while not self.done:
            self.event_loop()
            self.check_collider()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)
            self.countdown -= 1
            if self.countdown <= 0:
                self.done = True
        print('game over')

    def update(self):
        self.current_time = pg.time.get_ticks()
        self.mouse_pos = None
        self.mouse_click[0] = False
        self.mouse_click[1] = False
        self.bg_manager.update()
        self.gui.update(self.current_time)
        self.plant_manager.update()
        self.prop_manager.update()
        self.bullet_manager.update()
        self.zombie_manager.update(self.current_time)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_pos = pg.mouse.get_pos()
                self.mouse_click[0], _, self.mouse_click[1] = pg.mouse.get_pressed()
                print('pos:', self.mouse_pos, ' mouse:', self.mouse_click)
                
    def check_collider(self):
        plant_prop_collider = pg.sprite.groupcollide(self.plant_manager.plant_group, self.prop_manager.prop_group, False, True)
        if len(plant_prop_collider)>0:
            for player,props in plant_prop_collider.items():
                for prop in props:
                    player.add_energy() 
                
        bullet_zombie_collider = pg.sprite.groupcollide(self.zombie_manager.zombie_group, self.bullet_manager.bullet_group, False, True)
        if len(bullet_zombie_collider) > 0:
                for zombie,bullets in bullet_zombie_collider.items():
                    for bullet in bullets:
                        zombie.setDamage(bullet.damage, bullet.isIce)
        
        car_zombie_collider = pg.sprite.groupcollide(self.plant_manager.car_group, self.zombie_manager.zombie_group, False, False)
        if len(car_zombie_collider) > 0:
                for car,zombies in car_zombie_collider.items():
                    car.setWalk()
                    for zombie in zombies:
                        zombie.setDamage(zombie.health)
    
    def game_failed(self):
        self.audio_player.play_failed()
        
    def game_victory(self):
        self.audio_player.play_victory()
    
class BGManager:
    def __init__(self,gm):
        self.gm = gm
        self.bg_group = pg.sprite.Group()
        bg = sprite.BGSprite("resource/image/bg/Background_0.jpg", (0,0))
        bg.add(self.bg_group)
        
    def update(self):
        self.bg_group.update()
        self.bg_group.draw(self.gm.screen)
        
class PlantManage:
    def __init__(self,gm):
        self.gm = gm
        self.plant_group = pg.sprite.Group()
        self.car_group = pg.sprite.Group()
        # 创建玩家
        # self.player = sprite.PlayerSprite("resource/image/actor/Peashooter_0.png",(71,71),self.gm)
        self.player = sprite.PeaShooter("resource/image/actor/Peashooter_0.png",(230,150),self.gm)
        # 创建车
        index = 0
        while index < 5:
            index += 1
            car = sprite.Car(self.gm, 150, 50+100*index)
            self.car_group.add(car)
        self.player.add(self.plant_group)
    def update(self):
        self.plant_group.update()
        self.plant_group.draw(self.gm.screen)
        self.car_group.update()
        self.car_group.draw(self.gm.screen)
        
    # 切换成普通豌豆射手
    def switch_peashooter(self, center, energy):
        self.plant_group.empty()
        plant = sprite.PeaShooter("resource/image/actor/Peashooter_0.png",center, self.gm)
        plant.energy = energy
        plant.add(self.plant_group)
    
    # 切换成双发豌豆射手
    def switch_repeaterpea(self, center, energy):
        self.plant_group.empty()
        plant = sprite.RepeaterPea("resource/image/actor/RepeaterPea_0.png",center, self.gm)
        plant.energy = energy
        plant.add(self.plant_group)
        
    # 切换成寒冰豌豆射手
    def switch_snowpea(self, center, energy):
        self.plant_group.empty()
        plant = sprite.SnowPea("resource/image/actor/SnowPea_0.png",center, self.gm)
        plant.energy = energy
        plant.add(self.plant_group)
        
    # 切换成三发豌豆射手
    def switch_Threepeater(self,center,energy):
        self.plant_group.empty()
        plant =  sprite.Threepeater("resource/image/actor/Threepeater_0.png",center, self.gm)
        plant.energy = energy
        plant.add(self.plant_group)

# 物品    
class PropManager:
    def __init__(self,gm):
        self.gm = gm
        self.prop_group = pg.sprite.Group()
        self.time_count = 5
        
    def generate(self):
        x = random.randint(200,500)
        y  = random.randint(100,530)
        value = random.random()
        if value > 0.7:
            sprite.PropSprite("resource/image/actor/Sun_0.png", x, y, 1).add(self.prop_group)
        elif value > 0.4:
            sprite.PropSprite("resource/image/actor/Sun_0.png", x, y, 1).add(self.prop_group)
        else:
            sprite.PropSprite("resource/image/actor/Sun_0.png", x, y, 1).add(self.prop_group)
 
    def update(self):
        self.time_count -= 0.1
        if self.time_count <= 0:
            self.time_count = 10
            self.generate()
        self.prop_group.update()
        self.prop_group.draw(self.gm.screen)
        
# 子弹
class BulletManager:
    def __init__(self,gm):
        self.gm = gm
        # 子弹group
        self.bullet_group = pg.sprite.Group()
    
    def update(self):
        self.bullet_group.update()
        self.bullet_group.draw(self.gm.screen)
    
    # 发射豌豆
    def shoot(self, x, y):
        pea = sprite.Pea("resource/image/actor/PeaNormal_0.png",x,y)
        pea.add(self.bullet_group)
        
    # 发射冰豌豆
    def shoot_icepea(self,x,y):
        pea =sprite.Pea("resource/image/actor/Peaice_0.png",x,y)
        pea.damage = 3
        pea.isIce = True
        pea.add(self.bullet_group)
        
# 僵尸
class ZombieManager:
    def __init__(self,gm):
        self.gm = gm
        self.zombie_group = pg.sprite.Group()
        self.head_group = pg.sprite.Group()
        self.losthead_group = pg.sprite.Group()
        self.time_count = 1
        
    def update(self, current_ticks):
        self.time_count -= 0.1
        if self.time_count <= 0:
            self.time_count = max(20, 100 - current_ticks / self.gm.fps / 10)
            self.create()
        
        self.zombie_group.update(current_ticks)
        self.zombie_group.draw(self.gm.screen)
        self.head_group.update(current_ticks)
        self.head_group.draw(self.gm.screen)
        self.losthead_group.update(current_ticks)
        self.losthead_group.draw(self.gm.screen)
        
    def create(self):
        # zombie = sprite.Zombie("resource/image/actor/Zombie_0.png", 1, 1, self.gm)
        type = random.randint(1,5)
        x = 1000
        y = random.randint(100,550)
        if type == 1:
            zb = zombie.NormalZombie(self.gm, x,y,self.head_group)
        elif type == 2:
            zb = zombie.ConeHeadZombie(self.gm, x,y,self.head_group)
        elif type == 3:
            zb = zombie.BucketHeadZombie(self.gm, x,y,self.head_group)
        elif type == 4:
            zb = zombie.FlagZombie(self.gm, x,y,self.head_group)
        else:
            zb = zombie.NewspaperZombie(self.gm, x,y,self.head_group)
        zb.add(self.zombie_group)