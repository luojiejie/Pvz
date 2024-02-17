import os
import pygame as pg

class bgm_player():
    
    def play(self, bgm):
        bg_path = os.path.join("resource", "audio", "bg", bgm)
        pg.mixer.init()    # 初始化音频部分
        pg.mixer.music.load(bg_path) # 载入音乐，支持ogg、mp3等格式不过，MP3 并不是所有的系统都支持（Linux 默认就不支持 MP3 播放）
        pg.mixer.music.play(-1)          # 播放start
        
    def play_choose_bgm(self):
        self.play("bgm_choose.mp3")
    
    def play_bgm(self):
        self.play("bgm1.mp3")
        
class audio_player():
    
    def play(self, audio):
        sound_path = os.path.join("resource", "audio", "sound", audio)
        sound = pg.mixer.Sound(sound_path)
        sound.play()
        
    # 僵尸来了
    def play_zombie_coming(self):
        self.play("zombie coming.mp3")
        
    # 爆炸
    def play_boom(self):
        self.play("boom.mp3")
    
    # 失败
    def play_failed(self):
        self.play("failed.mp3")
    
    # 胜利 
    def play_victory(self):
        self.play("victory.mp3")
    
    # 大量僵尸来袭
    def play_many_zombies_coming(self):
        self.play("many zombies coming.mp3")
       
    # 僵尸吃 
    def play_zombie_eat(self):
        self.play("zombie eat.mp3")
    
    def stop_play_zombie_eat(self):
        self.play("zombie eat.mp3")
    
    # 僵尸笑
    def play_zombie_laungh(self):
        self.play("zombie laungh.mp3")
        