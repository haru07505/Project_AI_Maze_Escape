# class đối tượng  trong game
import pygame
from settings import TILE_SIZE
from utils import load_image


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("hard_level/picture/shadowwall.jpg", (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))


class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y, side):
        super().__init__()
        if side == 'L':
            self.image = load_image('hard_level/picture/portal_left.png', (TILE_SIZE, TILE_SIZE))
        elif side == 'R':
            self.image = load_image('hard_level/picture/portal_right.png', (TILE_SIZE, TILE_SIZE))
        else:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 0, 0))  # debug
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))  
        self.side = side


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("hard_level/picture/door.png", (TILE_SIZE, TILE_SIZE))  
        if self.image is None:
            print("Error: Door image not found!")  
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
