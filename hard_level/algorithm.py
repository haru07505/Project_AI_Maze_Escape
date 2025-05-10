# thuật toán của trò chơi
import heapq

class MazeAI:
    def __init__(self, maze_map, portal_dict, max_lives=10):
        self.original_map = [list(row) for row in maze_map] # map gốc
        self.reset_map()
        self.portals = portal_dict #ánh xạ cổng
        self.width = len(maze_map[0])
        self.height = len(maze_map)
        self.max_lives = max_lives
        self.current_enemies = [] # danh sách vị trí quái vật

    def reset_map(self): # cập nhật map
        self.map = [row.copy() for row in self.original_map]

    def is_in_bounds(self, x, y): # kiểm tra vị trí hợp lệ trong map
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x, y, has_weapon): #kiểm tra vị trí có đi qua được không
        tile = self.map[y][x]
        if tile == 'W':
            return False
        return True

    def get_neighbors(self, x, y, has_weapon, visited_portals=None): # lấy vị trí hàng xóm/ các ô lân cận
        neighbors = []
        if visited_portals is None:
            visited_portals = set()
        # duyệt  4 hướng trên dưới trái phải
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if self.is_in_bounds(nx, ny) and self.is_walkable(nx, ny, has_weapon):
                neighbors.append(((nx, ny), 0))
        # di chuyển qua cổng dịch chuyển
        if (x, y) in self.portals and (x, y) not in visited_portals:
            px, py = self.portals[(x, y)]
            neighbors.append(((px, py), 5))
        return neighbors

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def proximity_penalty(self, x, y, enemy_positions):
        penalty = 0
        for ex, ey in enemy_positions: # mahattan đến quái vật
            dist = abs(x - ex) + abs(y - ey)
            if dist <= 1: 
                penalty = max(penalty, 10)
            elif dist <= 2:
                penalty = max(penalty, 5)
        return penalty

    def simulate_enemy_positions(self): # dự đoán vị trí di chuyển của enemy
        possible_positions = set()
        for ex, ey in self.current_enemies:
            possible_positions.add((ex, ey))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = ex + dx, ey + dy
                if self.is_in_bounds(nx, ny) and self.map[ny][nx] != 'W':
                    possible_positions.add((nx, ny))
        return possible_positions

    def a_star(self, start, goals, has_weapon, visited_portals=None):
        if not goals:
            return []
        frontier = []
        heapq.heappush(frontier, (0, start, set()))
        came_from = {(start, frozenset()): None} # lưu lại đường đi
        cost_so_far = {(start, frozenset()): 0} # lưu chí phí đường đi
        goals_set = set(goals)
        enemy_positions = self.simulate_enemy_positions()

        while frontier:
            current_priority, current, visited_portals = heapq.heappop(frontier) # lấy ô có chi phí thấp nhất

            if current in goals_set: # tìm đường đến goal
                path = []
                state = (current, frozenset(visited_portals))
                while state:
                    pos, vp = state
                    path.append(pos)
                    state = came_from.get(state)
                path.reverse()
                return path
            # duyệt các ô lân cận
            for (next_pos, extra_cost) in self.get_neighbors(*current, has_weapon, visited_portals):
                new_visited_portals = set(visited_portals)
                if current in self.portals and current not in new_visited_portals:
                    new_visited_portals.add(current)
                tile = self.map[next_pos[1]][next_pos[0]]
                cost = 1 + extra_cost
                cost += self.proximity_penalty(next_pos[0], next_pos[1], enemy_positions)
                if tile == 'B': # chi phí nếu gặp bomb
                    cost += 50
                if tile == 'E' and not has_weapon: # tăng chi phí nếu gặp enemy và không có súng
                    cost += 1000
                elif tile == 'E' and has_weapon:
                    cost += 5
                #nếu đường đi mới tốt hơn, cập nhật đường đi mới
                new_cost = cost_so_far[(current, frozenset(visited_portals))] + cost
                new_state = (next_pos, frozenset(new_visited_portals))
                if new_state not in cost_so_far or new_cost < cost_so_far[new_state]:
                    cost_so_far[new_state] = new_cost
                    priority = new_cost + min(self.heuristic(next_pos, goal) for goal in goals) # ước lượng chi phí tới mục tiêu
                    heapq.heappush(frontier, (priority, next_pos, new_visited_portals))
                    came_from[new_state] = (current, frozenset(visited_portals))
        print(f"No path found from {start} to {goals}")
        return []

    def find_all_positions(self, tile_char):
        """Tìm tất cả vị trí của ký tự (G = gun, K = key, D = door)."""
        positions = []
        for y, row in enumerate(self.map):
            for x, char in enumerate(row):
                if char == tile_char:
                    positions.append((x, y))
        return positions

    def get_nearest_portal_exit(self, from_pos):
        """Tìm cổng dịch chuyển gần nhất từ vị trí hiện tại và trả về điểm đến."""
        min_dist = float('inf')
        nearest_exit = from_pos  # Mặc định không đi qua portal
        for entry, exit in self.portals.items():
            if entry != from_pos:  # Đảm bảo không chọn cổng mà mình đang đứng trên
                dist = self.heuristic(from_pos, entry)
                if dist < min_dist:
                    min_dist = dist
                    nearest_exit = exit
        return nearest_exit

    def find_path(self, start_pos, has_weapon, has_key):
   
        self.reset_map()  # Cập nhật bản đồ từ bản gốc để đảm bảo tính chính xác

        # Lấy danh sách các vị trí súng, chìa khóa và cửa
        gun_pos = self.find_all_positions('G')
        key_pos = self.find_all_positions('K')
        door_pos = self.find_all_positions('D')

        # Giai đoạn 3: Nếu đã có chìa khóa, chỉ cần tìm đường đến cửa
        if has_key:
            return self.a_star(start_pos, door_pos, has_weapon)

        # Giai đoạn 2: Nếu đã có súng, tìm đường đến chìa khóa → sau đó đến cửa
        if has_weapon:
            path_to_key = self.a_star(start_pos, key_pos, has_weapon=True)
            if not path_to_key:
                return []  # Không tìm được đường đến chìa khóa

            key_location = path_to_key[-1]
            self.map[key_location[1]][key_location[0]] = '.'  # Đánh dấu ô đã ghé qua

            path_to_door = self.a_star(key_location, door_pos, has_weapon=True)
            if not path_to_door:
                return []  # Không tìm được đường đến cửa

            return path_to_key + path_to_door[1:]  # Ghép đường

        # Giai đoạn 1: Nếu chưa có gì, tìm đường đến súng → cổng dịch chuyển → chìa khóa → cửa
        path_to_gun = self.a_star(start_pos, gun_pos, has_weapon=False)
        if not path_to_gun:
            return []  # Không tìm được đường đến súng

        gun_location = path_to_gun[-1]
        self.map[gun_location[1]][gun_location[0]] = '.'  # Đã ghé qua ô có súng

        # Sử dụng cổng dịch chuyển gần nhất để di chuyển nhanh hơn
        portal_exit = self.get_nearest_portal_exit(gun_location)

        # Tìm đường từ cổng đến chìa khóa (lúc này đã có súng)
        path_to_key = self.a_star(portal_exit, key_pos, has_weapon=True)
        if not path_to_key:
            return []

        key_location = path_to_key[-1]
        self.map[key_location[1]][key_location[0]] = '.'  # Đánh dấu đã ghé qua chìa khóa

        # Tìm đường từ chìa khóa đến cửa
        path_to_door = self.a_star(key_location, door_pos, has_weapon=True)
        if not path_to_door:
            return []

        # Ghép các đoạn đường lại, bỏ bước đầu của các đoạn sau để tránh lặp
        return path_to_gun + path_to_key[1:] + path_to_door[1:]
