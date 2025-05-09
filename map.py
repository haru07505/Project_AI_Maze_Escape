import pygame
import pytmx
import objects
from solve_maze import get_solution
from tkinter import messagebox
import time

class Game:
    def __init__(self, file_path, algorithm, width):
        self.running = False  # Ban đầu game chưa chạy
        self.WIDTH = width
        self.HEIGHT = 850
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Escape Game")
        if width == 720:
            self.map_matrix = [[0 for _ in range(15)] for _ in range(15)]
        elif width == 960:
            self.map_matrix = [[0 for _ in range(20)] for _ in range(20)]
        self.tmx_data = pytmx.load_pygame(file_path)
        self.door = pygame.image.load("door.png")
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight
        self.map_width = self.tmx_data.width * self.tile_width
        self.map_height = self.tmx_data.height * self.tile_height
        self.algorithm = algorithm
        self.all_sprites = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()
        self.started_game = False
        self.collected_key = False
        self.finised_game = False
        self.has_sword = False
        self.hard = False
        self.load_objects()
        self.load_matrix_map()
        self.font = pygame.font.SysFont('Arial', 18)
        self.sword_timer = False

    def load_objects(self):
        """ Xử lý objects layer và cập nhật ma trận """
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):  # Kiểm tra nếu là objects layer
                for obj in layer:  
                    grid_x = int(obj.x // self.tile_width)
                    grid_y = int(obj.y // self.tile_height)
                    if obj.name == "player":  
                        self.map_matrix[grid_y][grid_x] = 2
                    elif obj.name == "key":  
                        self.map_matrix[grid_y][grid_x] = 3
                    elif obj.name == "exit_gate":  
                        self.map_matrix[grid_y][grid_x] = 4
                        self.door_rect = self.door.get_rect(topleft=(grid_x * self.tile_width, grid_y * self.tile_height - 38))
                    elif obj.name == "sword":
                        self.map_matrix[grid_y][grid_x] = 5
                    elif obj.name == "bat":
                        self.map_matrix[grid_y][grid_x] = 6
                    elif obj.name == "skeleton":
                        self.map_matrix[grid_y][grid_x] = 7
    def load_matrix_map(self):
        for layer_index, layer in enumerate(self.tmx_data.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer) and layer_index == 1 :
                for x, y, gid in layer:                
                    if gid != 0:
                        self.map_matrix[y][x] = 1  # Đánh dấu vật cản
    def run(self):
        #current_step = 0
        """ Vòng lặp game """
        for y, row in enumerate(self.map_matrix):
            for x, cell in enumerate(row):
                if cell == 2:  # Nhân vật
                    self.player = objects.Player(self.map_matrix, self.tile_width, self.tile_height)
                    self.all_sprites.add(self.player)
                elif cell == 3:  # Chìa khóa
                    self.key = objects.Key((x * self.tile_width + self.tile_width // 2, y * self.tile_height))
                    self.all_sprites.add(self.key)   
                elif cell == 5:
                    self.sword = objects.Sword((x * self.tile_width + self.tile_width // 2, y * self.tile_height))
                    self.all_sprites.add(self.sword)
                    self.hard = True
                elif cell == 6:
                    self.bat = objects.Monster((x * self.tile_width + self.tile_width // 2, y * self.tile_height), "bat")
                    self.monsters.add(self.bat)
                elif cell == 7:
                    self.skeleton = objects.Monster((x * self.tile_width + self.tile_width // 2, y * self.tile_height), "skeleton")
                    self.monsters.add(self.skeleton)    
        self.running = True
        while self.running:
            self.screen.fill((255, 255, 255))  # Màu nền trắng
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.started_game:
                        self.started_game = True 
                        solution, visited_nodes, generated, elapsed_time = get_solution(self.map_matrix, self.algorithm) 
                        self.player.move_player(solution)
                        start_time = time.perf_counter()
                        end_time = None
                        current_step = 0
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_RETURN and self.finised_game:
                        self.reset_game()
            if not self.running:
                break
            self.all_sprites.update()
            self.monsters.update()
            self.draw_map()
            if self.started_game == False:
                self.nofication("Press SPACE to start the game")
            else:
                if solution:
                    #direction = ""
                    self.display_info(solution, visited_nodes, generated, elapsed_time)
                    if not self.finised_game:
                        moved = self.player.update_auto_move(self.map_matrix)   
                        if moved:
                            current_step += 1
                        if end_time is None:
                            execute_time = time.perf_counter() - start_time
                        else:
                            execute_time = end_time - start_time
                        progress = current_step / len(solution)

                    self.draw_progress(self.finised_game, progress, execute_time)
                    key_x = (self.key.rect.x + self.tile_width // 2) // self.tile_width
                    key_y = self.key.rect.y // self.tile_height
                    player_x = (self.player.rect.x + self.tile_width // 2) // self.tile_width
                    player_y = self.player.rect.y // self.tile_height
                    if self.hard:
                        sword_x = (self.sword.rect.x + self.tile_width // 2) // self.tile_width
                        sword_y = self.sword.rect.y // self.tile_height
                        if player_x == sword_x and player_y == sword_y:
                            self.has_sword = True
                            self.sword_timer = True
                            text_timer = time.perf_counter()
                    if player_x == key_x and player_y == key_y:
                        self.collected_key = True
                        text_timer = time.perf_counter()
                    if self.collected_key or self.has_sword:
                        if self.collected_key:
                            self.key.kill()  
                            self.nofication("You got the key!") 
                        elif self.sword_timer:
                            self.sword.kill()  
                            self.nofication("You got the sword!")
                        if time.perf_counter() - text_timer >= 0.5:
                            self.nofication("")
                            self.collected_key = False
                            self.sword_timer = False
                    move_dx, move_dy = 0, 0
                    direction = ""
                    if current_step < len(solution):
                        target_y, target_x = solution[current_step]
                        move_dx = target_x - player_x
                        move_dy = target_y - player_y
                        if move_dy == -2 and move_dx == 0:
                            direction = "up"
                        elif move_dy == 2 and move_dx == 0:
                            direction = "down"
                        elif move_dx == -1 and move_dy == 1:
                            direction = "left"
                        elif move_dx == 1 and move_dy == 1:
                            direction = "right"            
             
                        for monster in self.monsters:
                            
                            monster_x = (monster.rect.x + self.tile_width // 2) // self.tile_width
                            monster_y = (monster.rect.y + self.tile_height)// self.tile_height

                            if monster_x == target_x and monster_y == target_y and self.has_sword:
                                
                                current_time = time.perf_counter()
                                if monster.health > 0:
                                    if (current_time - monster.last_damage_time) * 1000 >= monster.damage_cooldown:
                                        self.player.attack(direction)
                                        monster.hurt()
                                        monster.last_damage_time = current_time
                                    if monster.health <= 0:
                                        monster.kill()
                                        self.monsters.remove(monster)
                                        self.player.attacking = False
                                        self.player.set_state(self.player.current_state)
                       
                    if player_x == self.door_rect.x // self.tile_width and player_y == self.door_rect.y // self.tile_height:
                        self.player.kill()
                        self.finised_game = True
                        end_time = time.perf_counter()
                        self.nofication("You completed the game! Press Enter to Reset or ESC to Exit.")
                else:
                    messagebox.showinfo("No Solution", "No solution found for the maze.")
                    self.started_game = False

            pygame.display.flip()
        
        pygame.quit()

    def draw_map(self):
        """ Vẽ map và các object """
        # Vẽ các layer trước objects (layer nền và layer thứ 2)
        for layer_index, layer in enumerate(self.tmx_data.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer) and layer_index < 2:
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        self.screen.blit(tile, (x * self.tile_width, y * self.tile_height))

        # Vẽ các objects
        for y, row in enumerate(self.map_matrix):
            for x, cell in enumerate(row):
                if cell == 2:  # Nhân vật
                    self.all_sprites.draw(self.screen)  
                elif cell == 3:  # Chìa khóa
                    self.all_sprites.draw(self.screen)
                elif cell == 5:  # Kiếm
                    self.all_sprites.draw(self.screen)
                elif cell == 6:  # Quái vật
                    self.monsters.draw(self.screen)
                elif cell == 7:  # Quái vật
                    self.monsters.draw(self.screen)

        # Vẽ layer thứ 3
        for layer_index, layer in enumerate(self.tmx_data.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer) and layer_index == 2:
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        self.screen.blit(tile, (x * self.tile_width, y * self.tile_height))

        if hasattr(self, 'door_rect'):
            self.screen.blit(self.door, self.door_rect.topleft)  

    def nofication(self, message):
        """ Hiển thị thông báo """
        font = pygame.font.Font(None, 36)
        text = font.render(message, True, (0, 0, 0))
        self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, self.HEIGHT // 2 - text.get_height() // 2 - 50))

    def display_info(self, solution, visited_nodes, generated, elapsed_time):
        text_visited = self.font.render(f"Visited nodes: {visited_nodes}", True, (0, 0, 0))
        text_time = self.font.render(f"Time to find solution: {elapsed_time}s", True, (0, 0, 0))
        text_path = self.font.render(f"Path length: {len(solution)}", True, (0, 0, 0))
        text_generated = self.font.render(f"Generated nodes: {generated}", True, (0, 0, 0))

        self.screen.blit(text_visited, (50, 730))
        self.screen.blit(text_generated, (250, 730))
        self.screen.blit(text_path, (50, 760))
        self.screen.blit(text_time, (250, 760))

    def draw_progress(self, done, progress, execute_time):
        """ Vẽ thanh tiến trình """
        text_ttime = self.font.render(f"Count time: {execute_time:2f}s", True, (0, 0, 0))
        step = self.font.render(f"{int(progress*100)}%", True, (0, 0, 0))
        self.screen.blit(step, (470, 820))
        if done:
            text = self.font.render("Done!", True, (0, 0, 0))
        else:
            text = self.font.render("Running...", True, (0, 0, 0))
        self.screen.blit(text, (50, 820))
        self.screen.blit(text_ttime, (50, 790))
        pygame.draw.rect(self.screen, (0, 255, 0), (145, 815, 310, 30), width=2)
        pygame.draw.rect(self.screen, (0, 175, 0), (150, 820, 300 * progress, 20))

    def reset_game(self):
        self.started_game = False
        self.finised_game = False
        self.collected_key = False
        self.has_sword = False
        self.load_objects()
        self.load_matrix_map()
        self.all_sprites.empty()
        self.monsters.empty()
        self.run()