import pygame
from settings import TILE_SIZE
from utils import load_sprite_sheet, load_image

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, portal, portal_dict):
        super().__init__()
        # vẽ nhân vật
        self.frames = load_sprite_sheet("hard_level/picture/Heroeplayer.png", 4, 4)
        self.frame_index = 0
        self.animation_frame = 0

        self.timer = 0

        self.heart_image = load_image("hard_level/picture/heart.png", (32, 32))
        # thời gian hòi chiêu
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 1000

        # mạng của ng chơi
        self.health = 5
        self.max_health = 5
        self.attack_damage = 10 # của enemy là 40 nên đánh 4 lần mới chết

        self.current_direction = 0 
        self.base_frame = self.frames[0]
        self.base_image = pygame.transform.scale(self.base_frame, (TILE_SIZE, TILE_SIZE))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        # danh sách cổng và từ điển ánh xạ giữa 2 cổng
        self.portals = portal
        self.portal_dict = portal_dict
        # trạng thái ban đầu của người chơi và vị trí 
        self.has_weapon = False
        self.has_key = False
        self.coin = 0
        self.weapon_img = None
        self.has_moved_since_teleport = False
        self.just_teleported = False
        self.x = x
        self.y = y

    def update(self):
        #cập nhật animation mỗi 10 frame
        self.timer += 1
        if self.timer % 10 == 0:
            self.animation_frame = (self.animation_frame + 1) % 4
            start_index = self.current_direction * 4
            self.frame_index = start_index + self.animation_frame
            self.base_frame = self.frames[self.frame_index]
            self.base_image = pygame.transform.scale(self.base_frame, (TILE_SIZE, TILE_SIZE))
        
        self.image = self.base_image.copy()
        #kiểm tra va chạm với cổng dịch chuyển
        for portal in self.portals:
            if self.rect.colliderect(portal.rect) and self.has_moved_since_teleport:
                self.teleport(portal)
                self.has_moved_since_teleport = False
                self.just_teleported = True
        # vẽ súng trên tay người chơi
        if self.has_weapon and self.weapon_img:
            offset_x = TILE_SIZE - self.weapon_img.get_width()
            offset_y = TILE_SIZE - self.weapon_img.get_height()
            self.image.blit(self.weapon_img, (offset_x, offset_y))
        # hét thời gian hồi chiêu
        if self.invincible and pygame.time.get_ticks() - self.invincible_timer > self.invincible_duration:
            self.invincible = False

    def teleport(self, portal): # ghép cổng/ dich chuyển đến cổng tương ứng
        other = self.portal_dict.get(portal)
        if other:
            self.rect.topleft = other.rect.topleft
            self.x = other.rect.left // TILE_SIZE
            self.y = other.rect.top // TILE_SIZE
            print(f"Teleported to ({self.x}, {self.y})")

    def is_dead(self): # kiểm tra mạng sống 
        return self.health <= 0

    def move(self, dx, dy, walls):
        new_rect = self.rect.move(dx * TILE_SIZE, dy * TILE_SIZE)
        if not any(wall.rect.colliderect(new_rect) for wall in walls):
            self.rect = new_rect
            self.x += dx
            self.y += dy
            self.has_moved_since_teleport = True
            self.just_teleported = False
            if dy == 1:
                self.current_direction = 0 #down
            elif dy == -1:
                self.current_direction = 1 # up
            elif dx == -1:
                self.current_direction = 2 # left
            elif dx == 1:
                self.current_direction = 3# right
            self.animation_frame = 0

    def attack(self, enemies): # hàm tấn công enemy
        if self.has_weapon:
            for enemy in enemies:
                if abs(self.x - enemy.x) + abs(self.y - enemy.y) <= 1:
                    enemy.take_damage(self.attack_damage)

    def take_damage(self, damage): # giảm mạng khi đụng bomb hoặc bị enemy tấn công
        if not self.invincible: 
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.kill()
                print("Player đã chết!")
            else:
                self.invincible = True # thời gian hồi chiêu
                self.invincible_timer = pygame.time.get_ticks()

    def draw_health(self, surface): # vẽ mạng sống
        for i in range(self.health):
            x = 10 + i * 36
            y = 10
            surface.blit(self.heart_image, (x, y))

    def pick_up(self, item): # nhặt vật phẩm
        if item.type == "gun":
            self.has_weapon = True
            self.weapon_img = load_image("hard_level/picture/gun.png", (TILE_SIZE // 2, TILE_SIZE // 2))
            print("Đã nhặt súng!")
        if item.type == "key":
            self.has_key = True
            print("Đã nhặt chìa khóa!")
        elif item.type == "coin":
            self.coin += 1
            print(f"Đã nhặt xu. Tổng xu: {self.coin}")

    '''===========================================
        # chế độ AI cho người chơi
    =============================================='''
    def set_ai_path(self, path):# tìm đường đi
        self.ai_path = path
        self.ai_step = 0

    def follow_ai_path(self, walls): # theo đường đã tìm
        if self.timer % 10 != 0:
            return
        if hasattr(self, 'ai_path') and self.ai_step < len(self.ai_path):
            target_x, target_y = self.ai_path[self.ai_step]
            if (self.x, self.y) == (target_x, target_y):
                self.ai_step += 1
                if self.ai_step >= len(self.ai_path):
                    return
            if self.ai_step < len(self.ai_path):
                target_x, target_y = self.ai_path[self.ai_step]
                dx = target_x - self.x
                dy = target_y - self.y
                if dx != 0:
                    dx = dx // abs(dx)
                if dy != 0:
                    dy = dy // abs(dy)
                self.move(dx, dy, walls)