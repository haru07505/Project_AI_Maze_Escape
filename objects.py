from tkinter import messagebox
import pygame
from collections import deque
import random


class Player(pygame.sprite.Sprite):
    def __init__(self, collision_map, tile_width, tile_height):
        super().__init__()
        self.collision_map = collision_map  # Lưu ma trận va chạm
        self.tile_width = tile_width  # Lưu chiều rộng ô
        self.tile_height = tile_height  # Lưu chiều cao ô
        # Load spritesheets with directions
        self.spritesheets = {
            "idle": self.load_sprites("sprite_sheet_idle_resized_48.png", 4, 15),
            "run": self.load_sprites("sprite_sheet_resized_48.png", 4, 15),
            "attack": self.load_sprites("sprite_sheet_attack_48.png", 4, 15)
        }
        
        self.state = "idle"
        self.direction = "down"  # Hướng mặc định
        self.index = 0
        self.image = self.spritesheets[self.state][self.direction][self.index]
        for y, row in enumerate(self.collision_map):
            for x, cell in enumerate(row):
                if cell == 2:
                    self.rect = self.image.get_rect(center=(x * tile_width + tile_width // 2, y * tile_height))
                    break
        self.animation_speed = 5
        self.counter = 0
        self.attacking = False
        #self.has_sword = False

    def load_sprites(self, file_path, num_directions, num_frames):
        """Cắt từng frame từ spritesheet, chia theo hướng"""
        spritesheet = pygame.image.load(file_path).convert_alpha()
        sprite_dict = {"down": [], "up": [], "left": [], "right": []}
        
        for row, direction in enumerate(sprite_dict.keys()):
            for i in range(num_frames):
                frame = spritesheet.subsurface((i * 48, row * 48, 48, 48))
                scaled_frame = pygame.transform.scale(frame, (96, 96))
                sprite_dict[direction].append(scaled_frame)
        
        return sprite_dict

    def set_state(self, new_state):
        """Chuyển trạng thái animation"""
        if self.state != new_state:
            self.state = new_state
            self.index = 0  

    def update(self):
        """Cập nhật animation"""
        self.counter += 1
        if self.counter >= self.animation_speed:
            self.counter = 0
            self.index = (self.index + 1) % len(self.spritesheets[self.state][self.direction])
            self.image = self.spritesheets[self.state][self.direction][self.index]


    def attack(self, direction):
        if not self.attacking:
            self.current_state = self.state
            self.attacking = True
            self.update_attack_direction(direction)  
            self.set_state("attack")
    
    def update_attack_direction(self, direction): 
        if direction == "down":
            self.direction = "down"
        elif direction == "up":
            self.direction = "up"
        elif direction == "left":
            self.direction = "left"
        elif direction == "right":
            self.direction = "right"

    def can_move_to(self, dx, dy):
        new_x = self.rect.x + dx 
        new_y = self.rect.y + dy 
        grid_x = int((new_x + self.tile_width // 2) // self.tile_width) 
        grid_y = int((new_y) // self.tile_height) + 1
        if 0 <= grid_x < len(self.collision_map[0]) and 0 <= grid_y < len(self.collision_map):
            if self.collision_map[grid_y][grid_x] in [0, 2, 3, 4]:
                return True
        return False
    
    def move_player(self, solution, delay=300):
        """Di chuyển nhân vật tự động theo solution mà không chặn luồng"""
        self.solution = deque(solution)  # Sử dụng deque để quản lý các bước
        self.last_move_time = pygame.time.get_ticks()  # Lưu thời gian bắt đầu
        self.move_delay = delay  # Thời gian delay giữa các bước
        
    def update_auto_move(self, maze):
        """Cập nhật vị trí nhân vật tự động"""
        if not self.attacking and self.state != "attack":
            if self.solution:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_move_time >= self.move_delay:
                    step = self.solution.popleft()
                    r, c = step    
                    dx, dy = 0, 0   
                    prev_pos = ((self.rect.y + self.tile_height)// self.tile_height, (self.rect.x + self.tile_width // 2) // self.tile_width)
                    # if maze[prev_pos[0]][prev_pos[1]] != 4:
                    maze[prev_pos[0]][prev_pos[1]] = 0  # Vị trí cũ quay lại thành "0"
                    maze[r][c] = 2  # Vị trí mới thành "2"           
                    if r > prev_pos[0]:  # Xuống
                        self.direction = "down"
                        self.set_state("run")
                        dy = self.tile_height
                    elif r < prev_pos[0]:  # Lên
                        self.direction = "up"
                        self.set_state("run")
                        dy = -self.tile_height
                    elif c > prev_pos[1]:  # Phải
                        self.direction = "right"
                        self.set_state("run")
                        dx = self.tile_width
                    elif c < prev_pos[1]:  # Trái
                        self.direction = "left"
                        self.set_state("run")
                        dx = -self.tile_width
                    self.rect.x += dx
                    self.rect.y += dy
                    self.last_move_time = current_time  # Cập nhật thời gian di chuyển
                    return True
            elif not self.solution:
                self.set_state("idle")   
        return False

class Monster(pygame.sprite.Sprite):
    def __init__(self, position, type_monster):
        super().__init__()
        if type_monster == "skeleton":
            self.sprites = self.load_idle_sprites("skeleton_idle.png", num_frames = 5)
            self.hurt_die_sprites = self.load_hurt_die_sprites("skeleton_hurt_die.png", num_frames = 11)
        elif type_monster == "bat":
            self.sprites = self.load_idle_sprites("bat_idle.png", num_frames = 4)
            self.hurt_die_sprites = self.load_hurt_die_sprites("bat_hurt_die.png", num_frames = 17)
        self.index = 0
        self.state = "idle"
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=position)
        self.animation_speed = 30
        self.counter = 0
        self.health = 3
        self.max_health = 3
        self.health_bar_length = 30  # Chiều dài thanh máu (pixels)
        self.health_bar_height = 5   # Chiều cao thanh máu
        self.health_bar_offset_y = -10  # Khoảng cách từ đỉnh quái vật
        #self.health_bar_color = (0, 255, 0)  # Màu xanh lá cho máu
        self.health_bar_bg_color = (255, 0, 0)  # Màu đỏ cho nền
        self.is_alive = True
        self.last_damage_time = 0
        self.damage_cooldown = 800
    def load_idle_sprites(self, file_path, num_frames):
        spritesheet = pygame.image.load(file_path).convert_alpha()
        sprite_frames = []

        for i in range(num_frames):
            frame = spritesheet.subsurface((i * 48, 0, 48, 48))
            if num_frames == 5:
                scaled_frame = pygame.transform.scale(frame, (72, 62))
                sprite_frames.append(scaled_frame)
            else:
                sprite_frames.append(frame)
        
        return sprite_frames
    
    def load_hurt_die_sprites(self, file_path, num_frames):
        spritesheet = pygame.image.load(file_path).convert_alpha()
        sprite_dict = {"hurt": [], "die": []}

        if num_frames == 11:
            for i in range(num_frames):
                frame = spritesheet.subsurface((i * 48, 0, 48, 48))
                scaled_frame = pygame.transform.scale(frame, (72, 72))
                if i < 5:
                    sprite_dict["hurt"].append(scaled_frame)
                else:
                    sprite_dict["die"].append(scaled_frame)
        elif num_frames == 17:
            for i in range(num_frames):
                frame = spritesheet.subsurface((i * 48, 0, 48, 48))
                if i < 7:
                    sprite_dict["hurt"].append(frame)
                else:
                    sprite_dict["die"].append(frame)
        
        return sprite_dict
    
    def update(self):
        self.counter += 1
        if self.counter >= self.animation_speed:
            self.counter = 0
            if self.state == "idle":
                self.index = (self.index + 1) % len(self.sprites)
                self.image = self.sprites[self.index]
            elif self.state == "hurt":
                self.index += 1
                self.image = self.hurt_die_sprites["hurt"][self.index]
                if self.index == len(self.hurt_die_sprites["hurt"]) - 1:
                    self.state = "idle"
                    self.index = 0
                    self.image = self.sprites[self.index]
                else:
                    self.image = self.hurt_die_sprites["hurt"][self.index]
            elif self.state == "die":
                self.index += 1
                if self.index == len(self.hurt_die_sprites["die"]) - 1:
                    self.is_alive = False
                else:
                    self.image = self.hurt_die_sprites["die"][self.index]

    def hurt(self):
        """Xử lý khi bị thương"""
        if self.is_alive and self.health > 0:
            self.health -= 1
            self.state = "hurt"
            self.index = 0
            self.image = self.hurt_die_sprites["hurt"][self.index]
            if self.health <= 0:
                self.die()
    
    def die(self):
        """Xử lý khi chết"""
        if self.is_alive:
            self.state = "die"
            self.index = 0
            self.image = self.hurt_die_sprites["die"][self.index]  

    def draw_health_bar(self, surface):
        """Vẽ thanh máu nếu quái vật còn sống và chưa chạy hết animation chết"""
        if not self.is_alive and self.state != "die":
            return

        health_ratio = max(0, self.health / self.max_health)
        health_width = self.health_bar_length * health_ratio

        # Thay đổi màu theo tỷ lệ máu
        if health_ratio > 0.6:
            health_color = (0, 255, 0)  # Xanh lá
        elif health_ratio > 0.3:
            health_color = (255, 255, 0)  # Vàng
        else:
            health_color = (255, 0, 0)  # Đỏ

        bar_x = self.rect.x + (self.rect.width - self.health_bar_length) // 2
        bar_y = self.rect.y + self.health_bar_offset_y

        # Vẽ nền
        pygame.draw.rect(surface, self.health_bar_bg_color,
                         (bar_x, bar_y, self.health_bar_length, self.health_bar_height))
        # Vẽ viền (tùy chọn)
        # Vẽ thanh máu
        if health_width > 0:
            pygame.draw.rect(surface, health_color, (bar_x, bar_y, health_width, self.health_bar_height))

class Key(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.sprites = self.load_sprites("key_32x32_24f.png", num_frames = 24)
        self.index = 0
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=position)
        self.animation_speed = 30
        self.counter = 0
    def load_sprites(self, file_path, num_frames = 24):
        """Cắt từng frame từ spritesheet"""
        spritesheet = pygame.image.load(file_path).convert_alpha()
        sprite_list = []
        for i in range(num_frames):
            frame = spritesheet.subsurface((i * 32, 0, 32, 32))
            sprite_list.append(frame)
        return sprite_list
    def update(self):
        """Cập nhật animation xoay vòng"""
        self.counter += 1
        if self.counter >= self.animation_speed:
            self.counter = 0
            self.index = (self.index + 1) % len(self.sprites)
            self.image = self.sprites[self.index]

class Sword(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.sprites = self.load_sprites("sword.png", num_frames = 8)
        self.index = 0
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=position)
        self.animation_speed = 30
        self.counter = 0
    def load_sprites(self, file_path, num_frames = 8):
        """Cắt từng frame từ spritesheet"""
        spritesheet = pygame.image.load(file_path).convert_alpha()
        sprite_list = []
        for i in range(num_frames):
            frame = spritesheet.subsurface((i * 48, 0, 48, 48))
            scaled_frame = pygame.transform.scale(frame, (32, 32))
            sprite_list.append(scaled_frame)
        return sprite_list
    def update(self):
        self.counter += 1
        if self.counter >= self.animation_speed:
            self.counter = 0
            self.index = (self.index + 1) % len(self.sprites)
            self.image = self.sprites[self.index]
