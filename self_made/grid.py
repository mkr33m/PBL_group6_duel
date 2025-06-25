from collections import deque
from typing import List, Tuple, Deque
from . import utils

N: int = 11
INF: int = 2 ** 20

def BFS(
        now_x: int,
        now_y: int,
        my_body_deq: Deque[Tuple[int, int]],
        opponent_body_deq: Deque[Tuple[int, int]],
        my_get_food: bool,
        opponent_get_food: bool,
        ) -> Tuple[List[List[int]], int]:
    
    vis_start = 0 # スタートを訪れた回数
    area: int = 0 # 到達可能なマスの数
    
    queue = deque()
    dist = [[INF] * N for _ in range(N)] # INF ではない -> 探索済み
    queue.append((now_x, now_y))
    dist[now_x][now_y] = 0
    start_x, start_y = now_x, now_y

    my_body_place = [[0] * N for _ in range(N)]
    idx = 1 + my_get_food
    for part in reversed(my_body_deq): # 尻尾から順に、番号を割り当てる
        my_body_place[part[0]][part[1]] = idx
        idx += 1
    
    opponent_body_place = [[0] * N for _ in range(N)]
    idx = -1 - opponent_get_food
    for part in reversed(opponent_body_deq):
        opponent_body_place[part[0]][part[1]] = idx
        idx -= 1

    while queue:
        
        x, y = queue.popleft()
        area += 1
        
        if (x, y) == (start_x, start_y):
            vis_start += 1
        
        for dir in range(4):
            next_x, next_y = x + utils.dx[dir], y + utils.dy[dir]
            
            if utils.out_of_grid(next_x, next_y):
                continue
            if dist[next_x][next_y] != INF and (next_x, next_y) != (start_x, start_y): # 探索済みならスキップ（ただし、始点は一旦スキップしない）
                continue
            if vis_start >= 2 and (x, y) == (start_x, start_y): # 始点は、すでに 2 回訪れているならスキップ
                continue
            
            if (my_body_place[next_x][next_y] == 0 or my_body_place[next_x][next_y] <= dist[x][y] + 1) and (opponent_body_place[next_x][next_y] == 0 or -opponent_body_place[next_x][next_y] <= dist[x][y] + 1):
                dist[next_x][next_y] = dist[x][y] + 1
                queue.append((next_x, next_y))
    
    return (dist, area)

def calc_dominant_space(
                        my_bfs: List[List[int]],
                        opponent_bfs: List[List[int]],
                        my_head_x: int,
                        my_head_y: int,
                        length_advantage: bool,
                        depth: int, # for debug
                        option: bool,
                        my_next_dir: int,
                        opponent_next_dir: int
                        ) -> int:

    my_dominant_space: int = -1  # 頭は除くから、その分を調整
    
    head_dist: int = my_bfs[my_head_x][my_head_y]
    my_bfs[my_head_x][my_head_y] = 0
    
    q: Deque[Tuple[int, int]] = deque()
    visited: List[List[bool]] = [[False] * N for _ in range(N)]
    q.append((my_head_x, my_head_y))
    visited[my_head_x][my_head_y] = True
    
    while q:
        x, y = q.popleft()
        my_dominant_space += 1
        
        for dir in range(4):
            nx, ny = x + utils.dx[dir], y + utils.dy[dir]
            
            if utils.out_of_grid(nx, ny):
                continue
            if visited[nx][ny]:
                continue
            if my_bfs[nx][ny] == INF:
                continue
            if length_advantage and my_bfs[nx][ny] > opponent_bfs[nx][ny]:
                continue
            if not length_advantage and my_bfs[nx][ny] >= opponent_bfs[nx][ny]:
                continue
            if not (my_bfs[nx][ny] <= my_bfs[x][y] + 1):
                continue

            visited[nx][ny] = True
            q.append((nx, ny))
    
    """ debug_list: List[List[str]] = [['x'] * N for _ in range(N)]
    
    if depth == 0 and option:
        file = open('debug.txt', 'a')
        
        file = open("debug.txt", "a")
        if option == 1:
            file.write("向き（自分、敵）: ")
        if option == 2:
            file.write("向き（敵、自分）: ")
        file.write(str(my_next_dir) + " ")
        file.write(str(opponent_next_dir) + '\n')
        
        if option == 1 : 
            file.write("my_dominant_space: ")
            file.write(str(my_dominant_space) + '\n')
        
        if option == 2:
            file.write("opponent_dominant_space: ")
            file.write(str(my_dominant_space) + '\n')
        
        for x in range(N):
            for y in range(N):
                if visited[x][y]:
                    debug_list[x][y] = 'o'
        
        for row in debug_list:
            line = ' '.join(map(str, row))  # 数字をスペース区切りの文字列に変換
            file.write(line + '\n')
        
        file.close() """
    
    my_bfs[my_head_x][my_head_y] = head_dist
    
    return my_dominant_space