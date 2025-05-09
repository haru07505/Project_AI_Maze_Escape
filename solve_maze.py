from collections import deque
from heapq import heappop, heappush
import random, math, time
import numpy as np

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def manhattan_distance(state, target):
    return abs(state[0] - target[0]) + abs(state[1] - target[1])

def bfs(maze, start):
    ROWS, COLS = len(maze), len(maze[0])
    queue = deque([(start, False, False, [])])
    visited = set()
    visited_nodes = 0
    generated_nodes = 1
    start_time = time.perf_counter()
    
    while queue:
        (r, c), has_key, has_sword, path = queue.popleft()
        path.append((r, c))
        
        tile = maze[r][c]
        if tile == 3:  
            has_key = True
        if tile == 5:
            has_sword = True
        if tile == 4 and has_key: 
            elapsed_time = time.perf_counter() - start_time 
            return path, visited_nodes, generated_nodes, elapsed_time
        state = (r, c, has_key, has_sword)
        if state in visited:
            continue
        visited.add(state)
        visited_nodes += 1
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                ntile = maze[nr][nc]
                if ntile in [0, 3, 5] or (has_key and ntile == 4) or (has_sword and ntile in [6, 7]):
                    queue.append(((nr, nc), has_key, has_sword, path[:]))
                    generated_nodes += 1
    elapsed_time = time.perf_counter() - start_time
    return path, visited_nodes, generated_nodes, elapsed_time

def a_start(maze, start, goal):
    ROWS, COLS = len(maze), len(maze[0])
    heap = []
    heappush(heap, (0, start, False, False, []))
    visited = set()
    visited_nodes = 0
    generated_nodes = 1
    start_time = time.perf_counter()

    while heap:
        f, (r, c), has_key, has_sword, path = heappop(heap)
        path.append((r, c))
        tile = maze[r][c]
        if tile == 3:  
            has_key = True
        if tile == 5:
            has_sword = True
        if tile == 4 and has_key:  
            elapsed_time = time.perf_counter() - start_time
            return path, visited_nodes, generated_nodes, elapsed_time
        state = (r, c, has_key, has_sword)
        if state in visited:
            continue
        visited.add(state)
        visited_nodes += 1

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                ntile = maze[nr][nc]
                if ntile in [0, 3, 5] or (has_key and ntile == 4) or (has_sword and ntile in [6, 7]):
                    g = len(path) + 1
                    h = manhattan_distance((nr, nc), goal)
                    heappush(heap, (g + h, (nr, nc), has_key, has_sword, path[:]))
                    generated_nodes += 1

    elapsed_time = time.perf_counter() - start_time
    return path, visited_nodes, generated_nodes, elapsed_time

def beam_search(maze, start, goal, beam_width=10):
    ROW, COLS = len(maze), len(maze[0])
    #queue = deque([(start, False, False, [])])
    frontier = [(manhattan_distance(start, goal), start, False, False, [])]
    visited = set()
    visited_nodes = 0
    generated_nodes = 1
    start_time = time.perf_counter()

    while frontier:
        next_frontier = []
        for _, (r, c), has_key, has_sword, path in frontier[:beam_width]:
            path.append((r, c))
            tile = maze[r][c]
            if tile == 3:  
                has_key = True
            if tile == 5:
                has_sword = True
            if tile == 4 and has_key:  
                elapsed_time = time.perf_counter() - start_time
                return path, visited_nodes, generated_nodes, elapsed_time
            state = (r, c, has_key, has_sword)
            if state in visited:
                continue
            visited.add(state)
            visited_nodes += 1

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROW and 0 <= nc < COLS:
                    ntile = maze[nr][nc]
                    if ntile in [0, 3, 5] or (has_key and ntile == 4) or (has_sword and ntile in [6, 7]):
                        next_frontier.append((manhattan_distance((nr, nc), goal), (nr, nc), has_key, has_sword, path[:]))
                        generated_nodes += 1

        frontier = sorted(next_frontier, key=lambda x: x[0])[:beam_width]

    elapsed_time = time.perf_counter() - start_time
    return path, visited_nodes, generated_nodes, elapsed_time

def backtracking(maze, start, goal):
    ROWS, COLS = len(maze), len(maze[0])
    path = []
    visited = set()
    has_key = False
    has_sword = False
    visited_nodes = 0
    generated_nodes = 1
    start_time = time.perf_counter()

    def solve(r, c):
        nonlocal has_key, has_sword, visited_nodes, generated_nodes, elapsed_time

        if (r, c) == goal:
            path.append((r, c))
            return True
        path.append((r, c))
        tile = maze[r][c]
        if tile == 3:  
            has_key = True
        if tile == 5:
            has_sword = True
        if tile == 4 and not has_key:  
            path.pop()
            return True
        if (tile == 6 or tile == 7) and not has_sword:
            path.pop()
            return True

        state = (r, c, has_key, has_sword)
        if state in visited:
            path.pop()
            return False
        visited.add(state)
        visited_nodes += 1

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                ntile = maze[nr][nc]
                if ntile in [0, 3, 5] or (has_key and ntile == 4) or (has_sword and ntile in [6, 7]):
                    generated_nodes += 1
                    if solve(nr, nc):
                        return True

        path.pop()
        return False
    
    if solve(start[0], start[1]):
        elapsed_time = time.perf_counter() - start_time
        return path, visited_nodes, generated_nodes, elapsed_time
    else:
        elapsed_time = time.perf_counter() - start_time
        return path, visited_nodes, generated_nodes, elapsed_time

def and_or_search(maze, start, goal):
    ROWS, COLS = len(maze), len(maze[0])
    visited = set()
    visited_nodes = 0
    generated_nodes = 1
    start_time = time.perf_counter()

    path = []

    def is_valid(r, c, has_key, has_sword):
        if 0 <= r < ROWS and 0 <= c < COLS:
            tile = maze[r][c]
            if tile in [0, 3, 5] or (has_key and tile == 4) or (has_sword and tile in [6, 7]):
                return True
        return False
    
    def move(r, c, dr, dc):
        return r + dr, c + dc
    
    def apply_action(belief_state, action):
        new_belief = set()
        for r, c, has_key, has_sword in belief_state:
            nr, nc = move(r, c, action[0], action[1])
            if is_valid(nr, nc, has_key, has_sword):
                has_key = has_key or maze[nr][nc] == 3
                has_sword = has_sword or maze[nr][nc] == 5
                new_belief.add((nr, nc, has_key, has_sword))
        return new_belief if new_belief  else None
    
    def all_goal(belief_state):
        return all((r, c) == goal for r, c, _, _ in belief_state)
    
    def or_search(belief_state, current_path):
        nonlocal visited_nodes, generated_nodes

        if not belief_state:
            return None
        
        if all_goal(belief_state):
            return current_path
        
        for r, c, has_key, has_sword in belief_state:
            state = (r, c, has_key, has_sword)
            if state in visited:
                continue
            visited.add(state)
            visited_nodes += 1
        
            for dr, dc in directions:
                new_belief = apply_action(belief_state, (dr, dc))
                if new_belief:
                    generated_nodes += 1
                    new_path = or_search(new_belief, current_path + [(r + dr, c + dc)])
                    if new_path:
                        return new_path  
                  
        return None
    
    path = or_search({(start[0], start[1], False, False)}, [start])
    elapsed_time = time.perf_counter() - start_time
    if path:
        return path, visited_nodes, generated_nodes, elapsed_time
    else:
        return [], visited_nodes, generated_nodes, elapsed_time

reward_map = {
    0: -1,  
    1: -100,   
    3: 5,   
    4: -10,  
    5: 5,  
    6: -10,  
    7: -10,  
}

def is_vaild(maze, r, c):
    ROWS, COLS = len(maze), len(maze[0])
    return 0 <= r < ROWS and 0 <= c < COLS

def q_learning(maze, start, goal, epsilon=0.2, alpha=0.1, gamma=0.9, episode=5000):
    ROWS, COLS = len(maze), len(maze[0])
    q_table = np.zeros((ROWS, COLS, 2, 2, len(directions)))  
    visited_nodes = 0
    generated_nodes = 1
    start_time = time.perf_counter()

    for i in range(episode):
        r, c = start
        has_key = False
        has_sword = False
        visited = set()
        step_count = 0
        max_steps = 1000  

        while (r, c) != goal and step_count < max_steps:
            step_count += 1
            generated_nodes += 1
            if (r, c) not in visited:
                visited.add((r, c))
                visited_nodes += 1

            if random.random() < epsilon:
                action = random.randint(0, 3)
            else:
                action = np.argmax(q_table[r][c][int(has_key)][int(has_sword)])
            
            dr, dc = directions[action]
            nr, nc = r + dr, c + dc

            if not is_vaild(maze, nr, nc):
                reward = -100  
                q_table[r][c][int(has_key)][int(has_sword)][action] += alpha * (reward - q_table[r][c][int(has_key)][int(has_sword)][action])
                continue
                
            tile = maze[nr][nc]
            reward = reward_map.get(tile, -1)  

            if tile == 4 and not has_key:
                reward = -50
                nr, nc = r, c
            elif tile in [6, 7] and not has_sword:
                reward = -50
                nr, nc = r, c
            elif tile == 3:
                has_key = True
                reward = -1
            elif tile == 5:
                has_sword = True
                reward = -1
            elif tile == 4 and has_key:
                reward = 100
            elif tile in [6, 7] and has_sword:
                reward = -1

            #reward += -0.1 * manhattan_distance((nr, nc), goal)

            max_future_q = np.max(q_table[nr][nc][int(has_key)][int(has_sword)])
            q_table[r][c][int(has_key)][int(has_sword)][action] += alpha * (reward + gamma * max_future_q - q_table[r][c][int(has_key)][int(has_sword)][action])

            r, c = nr, nc
        
        epsilon = max(0.05, epsilon * 0.995)
        if i % 1000 == 0:
            #print(f"Episode {i}, Epsilon: {epsilon}, Visited nodes: {visited_nodes}, Generated nodes: {generated_nodes}")
            path = get_path_from_q_table(q_table, maze, start, goal)
            if path and path[-1] == goal:
                #print(f"Found path in episode {i}: {path}")
                break
    
    elapsed_time = time.perf_counter() - start_time
    return q_table, visited_nodes, generated_nodes, elapsed_time

def get_path_from_q_table(q_table, maze, start, goal):
    r, c = start
    path = [start]
    has_key = False
    has_sword = False
    max_steps = 1000
    step = 0
    while (r, c) != goal and step < max_steps:
        step += 1
        action = np.argmax(q_table[r][c][int(has_key)][int(has_sword)])
        dr, dc = directions[action]
        nr, nc = r + dr, c + dc
        if not is_vaild(maze, nr, nc) or maze[nr][nc] == 1:
            break
        if maze[nr][nc] == 4 and not has_key:
            break
        if maze[nr][nc] in [6, 7] and not has_sword:
            break
        if maze[nr][nc] == 3:
            has_key = True
        if maze[nr][nc] == 5:
            has_sword = True

        path.append((nr, nc))
        r, c = nr, nc
    
    return path 
       
def get_solution(maze, algorithm):
    ROWS, COLS = len(maze), len(maze[0])
    start, goal = None, None
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == 2:
                start = (r, c)
            elif maze[r][c] == 4:
                goal = (r, c)   
    if algorithm == "BFS":
        return bfs(maze, start)
    elif algorithm == "A*":
        return a_start(maze, start, goal)
    elif algorithm == "Beam Search":
        return beam_search(maze, start, goal)
    elif algorithm == "Backtracking":
        return backtracking(maze, start, goal)
    elif algorithm == "And-Or Search":
        return and_or_search(maze, start, goal)
    elif algorithm == "Q-Learning":
        q_table, visited_nodes, generated_nodes, elapsed_time = q_learning(maze, start, goal)
        path = get_path_from_q_table(q_table, maze, start, goal)
        return path, visited_nodes, generated_nodes, elapsed_time

# def main():
#     # maze = [
#     #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#     #     [2, 0, 0, 0, 0, 3, 0, 0, 6, 1],
#     #     [1, 0, 1, 1, 0, 5, 0, 1, 4, 1],
#     #     [1, 0, 0, 0, 0, 6, 0, 7, 0, 1],
#     #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#     # ]
#     # maze = [
#     #     [2, 0, 0, 3],
#     #     [1, 0, 1, 0],
#     #     [4, 0, 0, 1]
#     # ]
#     maze = [
#         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
#         [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
#         [1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
#         [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
#         [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1],
#         [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1],
#         [1, 0, 0, 4, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1],
#         [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
#         [1, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
#         [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1],
#         [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1],
#         [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
#         [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#     ]
#     algorithm = "Q-Learning"  # Change this to test different algorithms
#     path, visited_nodes, generated_nodes, elapsed_time = get_solution(maze, algorithm)
#     print("Visted nodes:", visited_nodes)
#     print("Generated nodes:", generated_nodes)
#     print("Elapsed time:", elapsed_time)
#     print("Path:", path)

# if __name__ == "__main__":
#     main()