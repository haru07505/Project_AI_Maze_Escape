# vòng lặp chính của trò chơi
import threading
import time
import imageio
import numpy as np
import pygame
from tile import Wall, Portal, Door
from Player import Player
from Enemy import Enemy
from Item import Item
from settings import *
from algorithm import MazeAI

MAZE_MAP = [
    "WWWWWWWWWWWWWWWWWWWW",
    "WP..W..C....WC.G..BW",
    "W.W.W.WWWWW.W.WWW..W",
    "WCW.W.....W.W..RWE.W",
    "W.W.W.WWW.WBWWWWWW.W",
    "W.W.W.W.K.WE.CB...WW",
    "W.W.WEWEW.W.WWWWW..W",
    "W.W...W.WEW.W.B.WC.W",
    "W.WWWWW.W.W.W.W.WWWW",
    "W...C.W.W.W.W.W.W..W",
    "WWW.W.W.W.W.W.W.WW.W",
    "WC..W.W.W.C.W.W..E.W",
    "WBWWW.W.WWWWWWWWWWWW",
    "WL....W.....E...C.DW",
    "WWWWWWWWWWWWWWWWWWWW",
]

# W: wall
# .: đường đi
# E: enemy
# P: player
# C: coin
# G: gun
# D: door
# B: bomb
# L: portal left
# R: portal right 
# --- L - R là 1 cặp cổng dịch chuyển 

MAZE_WIDTH = len(MAZE_MAP[0])
MAZE_HEIGHT = len(MAZE_MAP)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((TILE_SIZE * MAZE_WIDTH, TILE_SIZE * MAZE_HEIGHT))
        pygame.display.set_caption("Maze Escape")

        self.clock = pygame.time.Clock()
        self.running = True
        self.HEIGHT = TILE_SIZE * MAZE_HEIGHT
        self.WIDTH = TILE_SIZE * MAZE_WIDTH
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.portals = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()

        self.portal_dict = {}
        self.player = None
        self.has_key = False
        self.game_won = False
        self.ai_mode = False # chế độ AI 

        self.collision_cooldown = 0
        self.collision_cooldown_duration = 50
        self.gif_frames = []
        self.ai_step_counter = 0
        self.ai_update_interval = 30
        self.load_level()
        self.maze_ai = MazeAI(MAZE_MAP, self.convert_portal_dict(), max_lives=15)
        self.init_ai_path()

    def convert_portal_dict(self):# chuyển portal từ object thành tọa độ 
        portal_coords = {}
        for portal1, portal2 in self.portal_dict.items():
            x1, y1 = portal1.rect.left // TILE_SIZE, portal1.rect.top // TILE_SIZE
            x2, y2 = portal2.rect.left // TILE_SIZE, portal2.rect.top // TILE_SIZE
            portal_coords[(x1, y1)] = (x2, y2)
            portal_coords[(x2, y2)] = (x1, y1)
        return portal_coords

    def init_ai_path(self): # Gọi tìm đường đi cho AI từ vị trí người chơi hiện tại
        if self.player and self.maze_ai:
            start_pos = (self.player.x, self.player.y)
            self.maze_ai.current_enemies = [(enemy.x, enemy.y) for enemy in self.enemies]
            path = self.maze_ai.find_path(start_pos, self.player.has_weapon, self.player.has_key)
            if path:
                self.player.set_ai_path(path)
                #print("AI path set:", path)
            else:
                print("Không tìm được đường đi cho AI.")

    def load_level(self):

        portal_left = None
        portal_right = None
        player_pos = None
        for y, row in enumerate(MAZE_MAP):
            for x, char in enumerate(row):
                if char == "W":
                    wall = Wall(x, y)
                    self.walls.add(wall)
                    self.all_sprites.add(wall)
                elif char == "P":
                    player_pos = (x, y)
                elif char == "L":
                    portal_left = Portal(x, y, 'L')
                    self.portals.add(portal_left)
                    self.all_sprites.add(portal_left)
                elif char == "R":
                    portal_right = Portal(x, y, 'R')
                    self.portals.add(portal_right)
                    self.all_sprites.add(portal_right)
                elif char == "D":
                    door = Door(x, y)
                    self.doors.add(door)
                    self.all_sprites.add(door)
                elif char == "K":
                    key = Item(x, y, "key")
                    self.items.add(key)
                    self.all_sprites.add(key)
                elif char == "C":
                    coin = Item(x, y, "coin")
                    self.items.add(coin)
                    self.all_sprites.add(coin)
                elif char == "B":
                    bomb = Item(x, y, "bomb")
                    self.items.add(bomb)
                    self.all_sprites.add(bomb)
                elif char == "G":
                    gun = Item(x, y, "gun")
                    self.items.add(gun)
                    self.all_sprites.add(gun)
                elif char == "E":
                    enemy = Enemy(x, y)
                    self.enemies.add(enemy)
                    self.all_sprites.add(enemy)
        # ghép 2 cổng dịch chuyển với nhau
        if portal_left and portal_right:
            self.portal_dict[portal_left] = portal_right
            self.portal_dict[portal_right] = portal_left
        if player_pos: # khởi tạo người chơi
            x, y = player_pos
            self.player = Player(x, y, self.portals, self.portal_dict)
            self.all_sprites.add(self.player)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.collision_cooldown > self.collision_cooldown_duration:
            self.collision_cooldown = 0

        for sprite in self.all_sprites:
            if isinstance(sprite, Enemy):
                sprite.update(self.walls, self.items, self.player)
            else:
                sprite.update()
        # AI =========================
        # nếu vừa dịch chuyển thì cập  nhật đường đi
        if self.ai_mode and self.player.just_teleported:
            self.player.just_teleported = False
            self.init_ai_path()
        #===============================
        # kiểm tra va chạm với enemy
        if self.collision_cooldown == 0:
            collided_enemies = pygame.sprite.spritecollide(self.player, self.enemies, dokill=False)
            for enemy in collided_enemies:
                self.player.take_damage(1)
                self.collision_cooldown = current_time
                if self.ai_mode:
                    self.init_ai_path()
        # nhặt vật phẩm
        collided_items = pygame.sprite.spritecollide(self.player, self.items, dokill=True)
        for item in collided_items:
            if item.type == "bomb" and self.collision_cooldown == 0:
                self.player.take_damage(1)
                print("Bị thương do đụng bom!")
                self.collision_cooldown = current_time
                if self.ai_mode:
                    self.init_ai_path()
            else:
                self.player.pick_up(item)
                if item.type in ["gun", "key"] and self.ai_mode:
                    self.init_ai_path()
        # kiểm tra va chạm với cửa
        collided_doors = pygame.sprite.spritecollide(self.player, self.doors, dokill=False)
        for door in collided_doors:
            if self.player.has_key:
                self.game_won = True
        # kiểm tra mạng
        if self.player.health <= 0:
            print("Game Over!")
            self.running = False
        #======================================AI
        if self.ai_mode:
            self.player.follow_ai_path(self.walls)
            if self.player.has_weapon:
                for enemy in self.enemies:
                    if abs(self.player.x - enemy.x) + abs(self.player.y - enemy.y) <= 1:
                        self.player.attack(self.enemies)
                        break
            self.ai_step_counter += 1
            if self.ai_step_counter >= self.ai_update_interval:
                self.ai_step_counter = 0
                self.init_ai_path()
        #======================================
    def draw(self):
        # vẽ màn hình game
        self.screen.fill(BLUE)
        self.all_sprites.draw(self.screen)
        self.player.draw_health(self.screen)
        for enemy in self.enemies: # vẽ máu enemy
            enemy.draw_health_bar(self.screen)
        # vẽ chữ khi thắng
        if self.game_won:
            font = pygame.font.SysFont(None, 72)
            text = font.render("You Escaped!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(text, text_rect)

       
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a: # bật tắt chế độ AI bằng phím a
                        self.ai_mode = not self.ai_mode
                        print("AI mode:", "ON" if self.ai_mode else "OFF")
                        if self.ai_mode:
                            self.init_ai_path()
                    if not self.ai_mode:
                        dx, dy = 0, 0
                        if event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                        elif event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1
                        elif event.key == pygame.K_SPACE: #đánh enemy bằng phím space
                            self.player.attack(self.enemies)
                        if dx != 0 or dy != 0:
                            self.player.move(dx, dy, self.walls)
            self.update()
            self.draw()
            self.clock.tick(60)