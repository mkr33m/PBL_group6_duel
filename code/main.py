from collections import deque
from typing import List, Tuple, Deque, Dict
import sys
import os

'''
6 班
Python 3.10.12
'''

# ./battlesnake play -t 2000 --name my_snake --url http://pbl.ics.es.osaka-u.ac.jp:10006 --name opponent_snake --url http://pbl.ics.es.osaka-u.ac.jp:10005 --browser
# ./battlesnake play --name my_snake --url http://localhost:8000 --name opponent_snake --url http://pbl.ics.es.osaka-u.ac.jp:10005 --browser

#########################################################################################################
def info() -> Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "my_snake",  # TODO: ユーザ名
        "color": "#39C5BB",  # TODO: 色
        "head": "ghost",  # TODO: 頭
        "tail": "wave",  # TODO: 尻尾
    }

current_dir = os.path.dirname(os.path.abspath(__file__)) # 現在のファイルのディレクトリ
parent_dir = os.path.abspath(os.path.join(current_dir, "..")) # 親ディレクトリ
sys.path.append(parent_dir) # モジュールの検索パスを追加

# 自作モジュールのインポート
import self_made.precalc
import self_made.utils
import self_made.grid

#########################################################################################################

N = 11
INF = 2 ** 20  # 無限大
dx = [1, 0, -1, 0]
dy = [0, 1, 0, -1]
RIGHT, UP, LEFT, DOWN = 0, 1, 2, 3
HEAD, BODY, TAIL = 1, 2, 3
direction = ["right", "up", "left", "down"]

my_prev_dir: int
my_prev_head_x: int
my_prev_head_y: int
my_prev_body_length: int
opponent_prev_dir: int
opponent_prev_head_x: int
opponent_prev_head_y: int
opponent_prev_body_length: int

def start(game_state: Dict):
    global my_prev_dir
    global my_prev_head_x
    global my_prev_head_y
    global my_prev_body_length
    global opponent_prev_dir
    global opponent_prev_head_x
    global opponent_prev_head_y
    global opponent_prev_body_length

    my_prev_dir = -1
    my_prev_head_x = -1
    my_prev_head_y = -1
    my_prev_body_length = 3
    opponent_prev_dir = -1
    opponent_prev_head_x = -1
    opponent_prev_head_y = -1
    opponent_prev_body_length = 3
    
    print("GAME START")

def end(game_state: Dict):
    print("GAME OVER")

# move 関数の返り値は、{"move" : 方向}（方向は、"right", "left", "up", "down" のいずれかの文字列）の辞書型
def move(game_state: Dict) -> Dict:
    
    global my_prev_dir
    global my_prev_head_x
    global my_prev_head_y
    global my_prev_body_length
    global opponent_prev_dir
    global opponent_prev_head_x
    global opponent_prev_head_y
    global opponent_prev_body_length
    
    # game_state からの情報を取得 ############################################################################
    my_head = game_state["you"]["head"]  # 自蛇の頭の座標
    my_body = game_state["you"]["body"]  # 自蛇の体の座標
    my_body_length = game_state["you"]["length"]  # 自蛇の体の長さ
    my_get_food = (my_body_length != my_prev_body_length) # 自蛇が餌を取った直後かどうか
    my_prev_body_length = my_body_length
    # 1 番目に格納されている蛇の情報が敵蛇じゃないなら、swap する
    if my_head == game_state["board"]["snakes"][1]["head"]:
        game_state["board"]["snakes"][0], game_state["board"]["snakes"][1] = \
            game_state["board"]["snakes"][1], game_state["board"]["snakes"][0]
    opponent_head = game_state["board"]["snakes"][1]["head"]  # 敵蛇の頭の座標
    opponent_body = game_state["board"]["snakes"][1]["body"]  # 敵蛇の体の座標
    opponent_body_length = game_state["board"]["snakes"][1]["length"]  # 敵蛇の体の長さ
    opponent_get_food = (opponent_body_length != opponent_prev_body_length)
    opponent_prev_body_length = opponent_body_length
    foods = game_state["board"]["food"]  # 餌の座標
    
    my_length_advantage: bool = (my_body_length > opponent_body_length)
    oppponent_length_advantage: bool = (opponent_body_length > my_body_length)
    
    if my_prev_head_x != -1:
        my_prev_dir = self_made.utils.find_direction(my_prev_head_x, my_prev_head_y, my_head["x"], my_head["y"])
    my_prev_head_x = my_head["x"]
    my_prev_head_y = my_head["y"]
    if opponent_prev_head_x != -1:
        opponent_prev_dir = self_made.utils.find_direction(opponent_prev_head_x, opponent_prev_head_y, opponent_head["x"], opponent_head["y"])
    opponent_prev_head_x = opponent_head["x"]
    opponent_prev_head_y = opponent_head["y"]

    my_body_deq: Deque[Tuple[int, int]] = deque() # 自蛇の体の位置を Deque で管理
    opponent_body_deq: Deque[Tuple[int, int]] = deque() # 敵蛇 .....
    snakes_body_state: List[List[int]] = [[0] * N for _ in range(N)] # 自蛇と敵蛇の体の位置を、二次元配列で管理
    foods_list: List[Tuple[int, int]] = []  # 餌の位置を保持するリスト
    foods_place: List[List[bool]] = [[False] * N for _ in range(N)] # 餌の位置を二次元 bool 型配列で管理
    for i in range(len(my_body)):
        my_body_deq.append((my_body[i]["x"], my_body[i]["y"]))
        snakes_body_state[my_body[i]["x"]][my_body[i]["y"]] = BODY
    for i in range(len(opponent_body)):
        opponent_body_deq.append((opponent_body[i]["x"], opponent_body[i]["y"]))
        snakes_body_state[opponent_body[i]["x"]][opponent_body[i]["y"]] = -BODY
    for i in range(len(foods)):
        foods_list.append((foods[i]["x"], foods[i]["y"]))
        foods_place[foods[i]["x"]][foods[i]["y"]] = True
    
    snakes_body_state[my_head["x"]][my_head["y"]] = HEAD
    snakes_body_state[my_body_deq[-1][0]][my_body_deq[-1][1]] = TAIL
    snakes_body_state[opponent_head["x"]][opponent_head["y"]] = -HEAD
    snakes_body_state[opponent_body_deq[-1][0]][opponent_body_deq[-1][1]] = -TAIL

    # 諸々の前計算 ###########################################################################################
    
    my_bfs, _ = self_made.grid.BFS(my_head["x"], my_head["y"], my_body_deq, opponent_body_deq, my_get_food, opponent_get_food)
    opponent_bfs, _ = self_made.grid.BFS(opponent_head["x"], opponent_head["y"], opponent_body_deq, my_body_deq, opponent_get_food, my_get_food)

    # 関数定義 ###############################################################################################
    
    # @brief 結果の出力
    def output_direction(next_dir: int) -> str:
        
        """ file = open('debug.txt', 'a') """
        
        # 結果の出力
        next_dir_str = direction[next_dir]
        print(f"MOVE {game_state['turn']}: {next_dir_str}")
        """ file.write(f"MOVE {game_state['turn']}: {next_dir_str}" + '\n') """
        
        """ file.close() """
        
        return next_dir_str


    # 実装 ###################################################################################################

    # 各方向について、敵蛇が常に最適（== 自蛇の支配領域を最小化する）ように動くときの、最終的な自蛇の支配領域
    my_dominant_space_list: List[int] = [-INF] * 4
    opponent_dominant_space_list: List[int] = [-INF] * 4
    
    my_fin_depth: int = 1
    opponent_fin_depth: int = 1
    
    my_valid_dir_list: List[bool] = [True] * 4
    opponent_valid_dir_list: List[bool] = [True] * 4
    
    for my_pad in range(-1, 2):
        my_next_dir = my_prev_dir + my_pad
        
        if my_next_dir >= 4:
            my_next_dir -= 4
        if my_next_dir < 0:
            my_next_dir += 4
        
        my_next_x, my_next_y = \
            my_head["x"] + dx[my_next_dir], my_head["y"] + dy[my_next_dir]
        
        if self_made.utils.out_of_grid(my_next_x, my_next_y):
            my_valid_dir_list[my_next_dir] = False
            continue
        
        for opponent_pad in range(-1, 2):
            opponent_next_dir = opponent_prev_dir + opponent_pad

            if opponent_next_dir >= 4:
                opponent_next_dir -= 4
            if opponent_next_dir < 0:
                opponent_next_dir += 4
            
            # 暫定的な、敵蛇の次の移動先
            opponent_next_x, opponent_next_y = \
                opponent_head["x"] + dx[opponent_next_dir], opponent_head["y"] + dy[opponent_next_dir]
            
            if self_made.utils.out_of_grid(opponent_next_x, opponent_next_y):
                opponent_valid_dir_list[opponent_next_dir] = False
                continue

            if (my_next_x, my_next_y) == (opponent_next_x, opponent_next_y):
                
                if not my_length_advantage:
                    my_valid_dir_list[my_next_dir] = False
                if not oppponent_length_advantage:
                    opponent_valid_dir_list[opponent_next_dir] = False
    
    my_valid_dir: int = my_valid_dir_list.count(True)
    opponent_valid_dir: int = opponent_valid_dir_list.count(True)
    
    if my_valid_dir >= 3:
        my_fin_depth = 4 - (game_state["turn"] < 200)
    elif my_valid_dir == 2:
        my_fin_depth = 5 - (game_state["turn"] < 200)
    else:
        my_fin_depth = 6 - (game_state["turn"] < 200)
    
    if opponent_valid_dir >= 3:
        opponent_fin_depth = 3
    elif opponent_valid_dir == 2:
        opponent_fin_depth = 4
    else:
        opponent_fin_depth = 5
    
    """ print("my_fin_depth :", my_fin_depth)
    print("opponent_fin_depth: ", opponent_fin_depth) """
    
    # 各進行方向について、自蛇の支配領域の予測計算
    self_made.precalc.precalc_dominant_space(
                                            snakes_body_state,
                                            foods_place,
                                            my_body_deq,
                                            opponent_body_deq,
                                            my_get_food,
                                            opponent_get_food,
                                            my_prev_dir,
                                            opponent_prev_dir,
                                            INF, # my_value_prod
                                            my_dominant_space_list,
                                            0, # depth
                                            my_fin_depth, # fin_depth
                                            -1, # first_dir
                                            0,
                                            )
    
    # 各進行方向について、敵蛇の支配領域の予測計算
    self_made.precalc.precalc_dominant_space(
                                            snakes_body_state,
                                            foods_place,
                                            opponent_body_deq,
                                            my_body_deq,
                                            opponent_get_food,
                                            my_get_food,
                                            opponent_prev_dir,
                                            my_prev_dir,
                                            INF, # opponent_value_min
                                            opponent_dominant_space_list,
                                            0, # depth
                                            opponent_fin_depth, # fin_depth
                                            -1, # first_dir
                                            1,
                                            )
    
    """ file = open('debug.txt', 'a')
    
    file.write("turn:")
    file.write(str(game_state["turn"]) + '\n')
    file.write("my_dominant_space_list: ")
    file.write(str(my_dominant_space_list) + '\n')
    file.write("opponent_dominant_space_list: ")
    file.write(str(opponent_dominant_space_list) + '\n')
    file.close() """

    
    ########## 勝ち確定方向が 2 種類あるとき -> BFS による面積が広い方向に進む
    if my_dominant_space_list.count(INF) > 1 or my_dominant_space_list.count(-INF) == 4:
        
        f: bool = (my_dominant_space_list.count(INF) > 1)
        
        my_decided_next_dir = -1
        my_max_area = -INF
        
        for my_pad in range(-1, 2):
            my_next_dir = my_prev_dir + my_pad
            
            if my_next_dir >= 4:
                my_next_dir -= 4
            if my_next_dir < 0:
                my_next_dir += 4
            
            if f and my_dominant_space_list[my_next_dir] != INF:
                continue
            
            my_next_x, my_next_y = \
                my_head["x"] + dx[my_next_dir], my_head["y"] + dy[my_next_dir]
            
            if self_made.utils.out_of_grid(my_next_x, my_next_y):
                continue
            if not my_get_food and snakes_body_state[my_next_x][my_next_y] == BODY: # 自分の胴体の当たり判定
                continue
            if my_get_food and BODY <= snakes_body_state[my_next_x][my_next_y] <= TAIL: # 自分の胴体の当たり判定
                continue
            if not opponent_get_food and snakes_body_state[my_next_x][my_next_y] == -BODY: # 敵の胴体の当たり判定
                continue
            if opponent_get_food and -TAIL <= snakes_body_state[my_next_x][my_next_y] <= -BODY: # 敵の胴体の当たり判定
                continue
            
            _, area = self_made.grid.BFS(my_next_x, my_next_y, my_body_deq, opponent_body_deq, my_get_food, opponent_get_food)
            
            if my_max_area < area:
                my_max_area = area
                my_decided_next_dir = my_next_dir
        
        assert my_decided_next_dir != -1
        
        """ file = open('debug.txt', 'a') # debug
        file.write("area_list: ")
        file.write(str(area_list) + '\n')
        file.close() """
        
        next_dir_str = output_direction(my_decided_next_dir)
        return {"move": next_dir_str}
    
    # 順位指定（降順ソートする） -> 方向取得
    val_and_dir: List[Tuple[int, int]] = [(-INF, -1), (-INF, -1), (-INF, -1), (-INF, -1)]
    
    for dir in range(4):
        val_and_dir[dir] = (my_dominant_space_list[dir], dir)
    
    val_and_dir.sort(reverse=True)
    
    # minval の降順で、方向に順位付けをする（方向指定 -> 順位取得）
    cnt_possible_dir: int = 0 # 正の val を持つ（少なくとも次手で詰むことは絶対にない）方向の数
    dir_rank: List[Tuple[int, int]] = [(INF, -1), (INF, -1), (INF, -1), (INF, -1)] # rank, sumval の tuple で持つ
    for val, dir in val_and_dir:
        if val <= 0:
            continue
        cnt_possible_dir += 1
        dir_rank[dir] = (cnt_possible_dir, val)
    
    """ file = open('debug.txt', 'a')
    
    file.write("my_dominant_space_list:")
    file.write(str(my_dominant_space_list) + '\n')
    file.write("opponent_dominant_space_list:")
    file.write(str(opponent_dominant_space_list) + '\n')
    file.write("val_and_dir: ")
    file.write(str(val_and_dir) + '\n')
    file.write("dir_rank: ")
    file.write(str(dir_rank) + '\n')
    
    file.close() """
    
    if max(opponent_dominant_space_list) < opponent_body_length: # 敵の支配領域が小さいときは攻めに行く
        my_next_dir = val_and_dir[0][1]
        next_dir_str = output_direction(my_next_dir)
        """ file = open('debug.txt', 'a')
        file.write("支配領域が最大の方向に進む" + '\n')
        file.close() """
        return {"move": next_dir_str}
    
    next_dir_str = ""
    
    nearest_food_x, nearest_food_y = -1, -1
    nearest_food_dist = INF
    opponent_nearest_food_dist = INF
    
    for food_x, food_y in foods_list:
        
        if nearest_food_dist > my_bfs[food_x][food_y]: # 自分にとって一番近い餌
            nearest_food_x, nearest_food_y = food_x, food_y
            nearest_food_dist = my_bfs[food_x][food_y]
        
        if opponent_nearest_food_dist > opponent_bfs[food_x][food_y]: # 敵にとって一番近い餌
            opponent_nearest_food_dist = opponent_bfs[food_x][food_y]
    
    diff_x, diff_y = nearest_food_x - my_head["x"], nearest_food_y - my_head["y"]
    
    fx: bool = (diff_x > 0) # x 軸正（RIGHT）方向に進むかどうか
    fy: bool = (diff_y > 0) # y 軸正（UP）方向に進むかどうか
    
    x_dir: int = RIGHT if fx else LEFT
    y_dir: int = UP if fy else DOWN
    
    """ file = open('debug.txt', 'a')
    file.write(str(fx) + '\n')
    file.write(str(fy) + '\n')
    file.close() """
    
    # x, y 方向がそれぞれ sumval の観点で上から何番目に属しているか？
    rank_x_dir, rank_x_val = dir_rank[x_dir]
    rank_y_dir, rank_y_val = dir_rank[y_dir]

    if rank_x_val >= max(my_body_length, 10) and rank_y_val >= max(my_body_length, 10):
        
        if (rank_x_dir < rank_y_dir and diff_x != 0) or diff_y == 0:
            next_dir_str = output_direction(x_dir)
        else:
            next_dir_str = output_direction(y_dir)
    
    elif rank_x_val >= max(my_body_length, 10) and diff_x != 0:
        next_dir_str = output_direction(x_dir)
    
    elif rank_y_val >= max(my_body_length, 10) and diff_y != 0:
        next_dir_str = output_direction(y_dir)
    
    if next_dir_str == "":
        my_next_dir = val_and_dir[0][1]
        next_dir_str = output_direction(my_next_dir)
    
    return {"move": next_dir_str}


if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})