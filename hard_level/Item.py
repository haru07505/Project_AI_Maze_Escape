# đại diện các object bomb, coin, gun
import pygame
from settings import TILE_SIZE
from utils import load_image

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, type_):
        super().__init__()
        path = f"hard_level/picture/{type_}.png"
        self.image = load_image(path, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        self.type = type_

    def update(self):
        # Không tự xử lý va chạm ở đây
        pass
