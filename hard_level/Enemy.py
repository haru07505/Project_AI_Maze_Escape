import pygame
import random
from settings import TILE_SIZE
from utils import load_sprite_sheet

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, direction="horizontal", distance=5, speed=1, max_hp=40):
        super().__init__()
        self.frames = load_sprite_sheet("hard_level/picture/goblin.png", 11, 4)
        self.frame_index = 0
        self.image = pygame.transform.scale(self.frames[0], (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))

        self.x = x
        self.y = y

        self.direction = direction
        self.move_dir = random.choice(["up", "down", "left", "right"])
        self.steps = 0
        self.distance = distance

        self.delay = random.randint(20, 60)  # frame delay
        self.timer = 0
        # máu enemy
        self.max_hp = max_hp
        self.hp = max_hp

    def update(self, walls, bombs, player):
        self.timer += 1
        if self.timer < self.delay:
            return
        self.timer = 0
        self.delay = random.randint(20, 60)

        dx, dy = 0, 0
        if self.move_dir == "up":
            dy = -1
        elif self.move_dir == "down":
            dy = 1
        elif self.move_dir == "left":
            dx = -1
        elif self.move_dir == "right":
            dx = 1
        # tính vị trí mới 
        new_x = self.x + dx
        new_y = self.y + dy
        new_rect = self.rect.move(dx * TILE_SIZE, dy * TILE_SIZE)
        #kiểm tra va chạm với tường và bomb
        if not any(w.rect.colliderect(new_rect) for w in walls) and \
           not any(b.rect.colliderect(new_rect) for b in bombs):
            # không có thì đi tiếp
            self.rect = new_rect
            self.x = new_x
            self.y = new_y
            self.steps += 1
        else:
            # Va chạm thì chọn hướng khác
            self.move_dir = random.choice(["up", "down", "left", "right"])
            self.steps = 0
        # giới hạn số bước
        if self.steps >= self.distance:
            self.move_dir = random.choice(["up", "down", "left", "right"])
            self.steps = 0

        # Cập nhật hoạt ảnh
        self.frame_index = (self.frame_index + 1) % 11
        dir_map = {"down": 0, "right": 1, "up": 2, "left": 3}
        row = dir_map[self.move_dir]
        frame_id = row * 11 + self.frame_index
        self.image = pygame.transform.scale(self.frames[frame_id], (TILE_SIZE, TILE_SIZE))

    def take_damage(self, damage):# bị thương khi bị tấn công
        self.hp -= damage # giảm máu
        if self.hp <= 0:
            self.kill() # =0 xóa quái
            print(f"Kẻ thù tại ({self.x}, {self.y}) đã bị tiêu diệt!")
    #vẽ thanh máu của quái vật
    def draw_health_bar(self, surface):
        bar_width = TILE_SIZE
        bar_height = 5
        fill = (self.hp / self.max_hp) * bar_width
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, fill, bar_height))
