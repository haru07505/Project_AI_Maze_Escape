# load ảnh mấy cái item/object
import pygame

def load_image(path, size=None):
    image = pygame.image.load(path).convert_alpha()
    if size:
        image = pygame.transform.scale(image, size)
    return image

def load_sprite_sheet(path, columns, rows, colorkey=None):
    sheet = pygame.image.load(path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // columns
    frame_height = sheet_height // rows

    frames = []
    for row in range(rows):
        for col in range(columns):
            x = col * frame_width
            y = row * frame_height
            frame = sheet.subsurface((x, y, frame_width, frame_height)).copy()
            if colorkey:
                frame.set_colorkey(colorkey)
            frames.append(frame)
    return frames
