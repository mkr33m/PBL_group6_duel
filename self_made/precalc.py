from typing import List, Tuple, Deque, Dict

from . import grid
from . import utils

NONE, HEAD, BODY, TAIL = 0, 1, 2, 3
INF = 2 ** 20

def deque_one_move_ahead(
                        body_deq: Deque[Tuple[int, int]],
                        get_food: bool,
                        foods_place: List[List[bool]],
                        next_x: int,
                        next_y: int,
                        depth: int,
                        ) -> Tuple[bool, int, int]:
    
    body_deq.appendleft((next_x, next_y))
    
    tail_x, tail_y = body_deq[-1]
    will_get_food: bool = False # 直後に餌を取るかどうかのフラグ
    
    if not get_food or depth == 0:
        body_deq.pop() # 直前に餌を取っていない -> 尻尾を動かす
    
    if foods_place[next_x][next_y]:
        will_get_food = True
        foods_place[next_x][next_y] = False
    
    return (will_get_food, tail_x, tail_y)

def body_state_one_move_ahead(
                            snakes_body_state: List[List[int]],
                            head_x: int,
                            head_y: int,
                            tail_x: int,
                            tail_y: int,
                            body_deq: Deque[Tuple[int, int]], # 一手先の deque
                            get_food: bool,
                            option: int,
                            ) -> None:

    if not get_food:
        if snakes_body_state[tail_x][tail_y] == (TAIL if option == 0 else -TAIL):
            snakes_body_state[tail_x][tail_y] = NONE
        snakes_body_state[body_deq[-1][0]][body_deq[-1][1]] = (TAIL if option == 0 else -TAIL)
    
    snakes_body_state[head_x][head_y] = (BODY if option == 0 else -BODY)
    snakes_body_state[body_deq[0][0]][body_deq[0][1]] = (HEAD if option == 0 else -HEAD)

def deque_one_move_behind(
                        body_deq: Deque[Tuple[int, int]],
                        tail_x: int,
                        tail_y: int,
                        get_food: bool,
                        will_get_food: bool,
                        foods_place: List[List[bool]],
                        depth: int
                        ) -> None:
    
    if will_get_food:
        foods_place[body_deq[0][0]][body_deq[0][1]] = True
    
    body_deq.popleft() # 頭を消す
    
    if not get_food or depth == 0:
        body_deq.append((tail_x, tail_y)) # deque から尻尾を消しているなら、元に戻す

def body_state_one_move_behind(
                        snakes_body_state: List[List[int]],
                        head_x: int,
                        head_y: int,
                        tail_x: int,
                        tail_y: int,
                        body_deq: Deque[Tuple[int, int]], # 一手先の deque
                        get_food: bool,
                        option: int,
                        ) -> None:
    
    if not get_food:
        snakes_body_state[body_deq[-1][0]][body_deq[-1][1]] = (BODY if option == 0 else -BODY)
        snakes_body_state[tail_x][tail_y] = (TAIL if option == 0 else -TAIL)
    
    if (snakes_body_state[body_deq[0][0]][body_deq[0][1]] == (HEAD if option == 0 else -HEAD)):
        snakes_body_state[body_deq[0][0]][body_deq[0][1]] = NONE
    snakes_body_state[head_x][head_y] = (HEAD if option == 0 else -HEAD)



def precalc_dominant_space(
                            snakes_body_state: List[List[int]],
                            foods_place: List[List[bool]],
                            my_body_deq: Deque[Tuple[int, int]],
                            opponent_body_deq: Deque[Tuple[int, int]],
                            my_get_food: bool, # 現時点、自蛇が餌を取った直後か？
                            opponent_get_food: bool,  # 現時点、敵蛇が餌を取った直後か？
                            my_prev_dir: int,
                            opponent_prev_dir: int,
                            my_value_prod: int,
                            my_value_prod_list: List[int],
                            depth: int, # 現在の再帰の深さ
                            fin_depth: int, # 再帰の深さ（何手先まで先読みするか？）
                            first_dir: int, # 初手でどの方向に進行したか
                            option: int,
                            ) -> None:
    
    if depth == fin_depth: # 終了
        
        """ if my_value_prod == INF:
            file = open("debug.txt", "a")
            file.write("勝ち確定？（ベースケース）" + '\n')
            file.write("option: ")
            file.write(str(option) + '\n')
            for row in snakes_body_state:
                line = ' '.join(map(str, row))  # 数字をスペース区切りの文字列に変換
                file.write(line + '\n')
            
            file.close() """
        
        my_value_prod_list[first_dir] = max(my_value_prod_list[first_dir], my_value_prod)
        
        return
    
    my_head_x, my_head_y = my_body_deq[0]
    opponent_head_x, opponent_head_y = opponent_body_deq[0]
    
    # 頭の衝突による禁止方向の処理
    my_prohibited_dir_list: List[bool] = [False] * 4
    opponent_prohibited_dir_list: List[bool] = [False] * 4
    
    # ここで、禁止方向を処理しておく
    for my_pad in range(-1, 2):
        my_next_dir = my_prev_dir + my_pad
        if my_next_dir < 0:
            my_next_dir += 4
        if my_next_dir >= 4:
            my_next_dir -= 4
        
        # 暫定的な、自蛇の次の移動先
        my_next_x, my_next_y = \
            my_head_x + utils.dx[my_next_dir], my_head_y + utils.dy[my_next_dir]
        
        for opponent_pad in range(-1, 2):
            opponent_next_dir = opponent_prev_dir + opponent_pad
            if opponent_next_dir < 0:
                opponent_next_dir += 4
            if opponent_next_dir >= 4:
                opponent_next_dir -= 4
            
            # 暫定的な、敵蛇の次の移動先
            opponent_next_x, opponent_next_y = \
                opponent_head_x + utils.dx[opponent_next_dir], opponent_head_y + utils.dy[opponent_next_dir]
            
            if (my_next_x, my_next_y) == (opponent_next_x, opponent_next_y):
                
                if len(my_body_deq) <= len(opponent_body_deq):
                    my_prohibited_dir_list[my_next_dir] = True
                if len(opponent_body_deq) <= len(my_body_deq):
                    opponent_prohibited_dir_list[opponent_next_dir] = True
    
    for my_pad in range(-1, 2): ##################### 自蛇の進行方向を固定
        
        my_next_dir = my_prev_dir + my_pad
        if my_next_dir < 0:
            my_next_dir += 4
        if my_next_dir >= 4:
            my_next_dir -= 4
        
        # 暫定的な、自蛇の次の移動先
        my_next_x, my_next_y = \
            my_head_x + utils.dx[my_next_dir], my_head_y + utils.dy[my_next_dir]
        
        first_dir_arg = first_dir
        if first_dir_arg == -1:
            first_dir_arg = my_next_dir
        
        # 自蛇の禁止方向の処理
        if utils.out_of_grid(my_next_x, my_next_y):
            continue
        if my_prohibited_dir_list[my_next_dir]:
            continue
        if not my_get_food and snakes_body_state[my_next_x][my_next_y] == (BODY if option == 0 else -BODY): # 自分の胴体の当たり判定
            continue
        if my_get_food and (BODY if option == 0 else -TAIL) <= snakes_body_state[my_next_x][my_next_y] <= (TAIL if option == 0 else -BODY): # 自分の胴体の当たり判定
            continue
        if not opponent_get_food and snakes_body_state[my_next_x][my_next_y] == (-BODY if option == 0 else BODY): # 敵の胴体の当たり判定
            continue
        if opponent_get_food and (-TAIL if option == 0 else BODY) <= snakes_body_state[my_next_x][my_next_y] <= (-BODY if option == 0 else TAIL): # 敵の胴体の当たり判定
            continue
        
        # 自蛇の deque を一手先の状態に更新
        my_will_get_food, my_tail_x, my_tail_y = deque_one_move_ahead(my_body_deq, my_get_food, foods_place, my_next_x, my_next_y, depth)
        
        my_min_value: int = INF # 敵蛇にとって、自蛇の支配領域を最小化する方向
        opponent_max_value: int = -INF
        opponent_max_value_assume: int = -INF # 敵蛇にとって、敵蛇の支配領域を最大化する方向（ただし、敵蛇の進行方向が存在しない場合）
        my_value_list: List[int] = []
        opponent_value_list: List[int] = [] # debug
        opponent_decided_dir: int = -1 # 自蛇の支配領域を最小化する方向
        opponent_most_expand_dir: int = -1
        opponent_most_expand_dir_assume: int = -1 # 敵蛇の支配領域を最大化する方向（ただし、敵蛇の進行方向が存在しない場合）
        
        opponent_safer_dir_list : List[int] = [] # 敵にとって安全な進行方向がないとき、まだ可能性があるような方向
        
        for opponent_pad in range(-1, 2): #################### 敵蛇の進行方向を確定させる -> 自蛇の支配領域を小さくする方向
            
            opponent_next_dir = opponent_prev_dir + opponent_pad
            if opponent_next_dir < 0:
                opponent_next_dir += 4
            if opponent_next_dir >= 4:
                opponent_next_dir -= 4
            
            # 暫定的な、敵蛇の次の移動先
            opponent_next_x, opponent_next_y = \
                opponent_head_x + utils.dx[opponent_next_dir], opponent_head_y + utils.dy[opponent_next_dir]
            
            # 敵蛇の禁止方向の処理
            if utils.out_of_grid(opponent_next_x, opponent_next_y): # 範囲外に出る
                continue
            if not my_get_food and snakes_body_state[opponent_next_x][opponent_next_y] == (BODY if option == 0 else -BODY): # 自蛇の胴体の当たり判定
                continue
            if my_get_food and (BODY if option == 0 else -TAIL) <= snakes_body_state[opponent_next_x][opponent_next_y] <= (TAIL if option == 0 else -BODY): # 自蛇の胴体の当たり判定
                continue
            if not opponent_get_food and snakes_body_state[opponent_next_x][opponent_next_y] == (-BODY if option == 0 else BODY): # 敵蛇の胴体の当たり判定
                continue
            if opponent_get_food and (-TAIL if option == 0 else BODY) <= snakes_body_state[opponent_next_x][opponent_next_y] <= (-BODY if option == 0 else TAIL): # 敵蛇の胴体の当たり判定
                continue
            if len(my_body_deq) >= len(opponent_body_deq) and (opponent_next_x, opponent_next_y) == (my_next_x, my_next_y): # head_to_head -> すり抜ける場合を考える
                if len(my_body_deq) != len(opponent_body_deq):
                    opponent_safer_dir_list.append(opponent_next_dir)
                continue
            
            # 自蛇の snakes_body_state を一手先の状態に更新
            body_state_one_move_ahead(snakes_body_state, my_head_x, my_head_y, my_tail_x, my_tail_y, my_body_deq, my_get_food, option)
            
            # 敵蛇の deque, snakes_body_state を一手先の状態に更新
            opponent_will_get_food, opponent_tail_x, opponent_tail_y = deque_one_move_ahead(opponent_body_deq, opponent_get_food, foods_place, opponent_next_x, opponent_next_y, depth)
            body_state_one_move_ahead(snakes_body_state, opponent_head_x, opponent_head_y, opponent_tail_x, opponent_tail_y, opponent_body_deq, opponent_get_food, 1 - option)
            
            # （暫定的な）体の長さで有利であるかどうかのフラグ
            my_next_length_advantage: bool = (len(my_body_deq) > len(opponent_body_deq))
            opponent_next_length_advantage: bool = (len(opponent_body_deq) > len(my_body_deq))
            
            # 次の BFS 盤面を生成する
            my_next_bfs, _ = grid.BFS(my_next_x, my_next_y, my_body_deq, opponent_body_deq, my_will_get_food, opponent_will_get_food)
            opponent_next_bfs, _ = grid.BFS(opponent_next_x, opponent_next_y, opponent_body_deq, my_body_deq, opponent_will_get_food, my_will_get_food)
            
            """ if depth == 0:
                
                file = open("debug.txt", "a")
                file.write("向き（自分、敵）: ")
                file.write(str(my_next_dir) + " ")
                file.write(str(opponent_next_dir) + '\n')
                file.write("option:")
                file.write(str(option) + '\n')
                file.write("my_next_bfs:" + '\n')
                for row in my_next_bfs:
                    line = ' '.join(map(str, row))  # 数字をスペース区切りの文字列に変換
                    file.write(line + '\n')
                file.write("opponent_next_bfs:" + '\n')
                for row in opponent_next_bfs:
                    line = ' '.join(map(str, row))  # 数字をスペース区切りの文字列に変換
                    file.write(line + '\n')
                
                file.close() """
            
            # 現在の支配領域を加算
            my_value = grid.calc_dominant_space(my_next_bfs, opponent_next_bfs, my_next_x, my_next_y, my_next_length_advantage, depth, 1, my_next_dir, opponent_next_dir)
            my_value_list.append(my_value)
            opponent_value = grid.calc_dominant_space(opponent_next_bfs, my_next_bfs, opponent_next_x, opponent_next_y, opponent_next_length_advantage, depth, 2, opponent_next_dir, my_next_dir)
            opponent_value_list.append(opponent_value) # debug
            
            if opponent_prohibited_dir_list[opponent_next_dir] or opponent_value < len(opponent_body_deq):
                # 敵蛇の支配領域が max となる方向も、一応記録しておく（敵蛇が禁止方向に進んだとき、どれくらい支配領域を広げるかを記録）
                if opponent_max_value_assume < opponent_value:
                    opponent_max_value_assume = opponent_value
                    opponent_most_expand_dir_assume = opponent_next_dir
            
            # 自蛇の支配領域が min となる方向を、敵の方向として確定させる
            elif opponent_value >= len(opponent_body_deq) and my_min_value > my_value:
                my_min_value = my_value
                opponent_decided_dir = opponent_next_dir
                if opponent_max_value < opponent_value:
                    opponent_max_value = opponent_value
                    opponent_most_expand_dir = opponent_next_dir
            
            # 敵蛇の deque、snakes_body_state を元に戻す
            body_state_one_move_behind(snakes_body_state, opponent_head_x, opponent_head_y, opponent_tail_x, opponent_tail_y, opponent_body_deq, opponent_get_food, 1 - option)
            deque_one_move_behind(opponent_body_deq, opponent_tail_x, opponent_tail_y, opponent_get_food, opponent_will_get_food, foods_place, depth)
            
            # 自蛇の snakes_body_state を元に戻す
            body_state_one_move_behind(snakes_body_state, my_head_x, my_head_y, my_tail_x, my_tail_y, my_body_deq, my_get_food, option)
        
        opponent_safe: bool = False
        
        ############################## 敵にとって安全な進行方向が存在しないときの処理 -> 敵蛇が
        if opponent_decided_dir == -1:
            
            if opponent_most_expand_dir_assume != -1:
                opponent_decided_dir = opponent_most_expand_dir_assume
                my_min_value = min(my_value_list) # 敵蛇の支配領域が最大化 == 自蛇の支配領域が最小化 に注意する
            
            else:
                for opponent_safer_dir in opponent_safer_dir_list:
                    opponent_safer_x, opponent_safer_y = \
                        opponent_head_x + utils.dx[opponent_safer_dir], opponent_head_y + utils.dy[opponent_safer_dir]
                    
                    if (opponent_safer_x, opponent_safer_y) != (my_next_x, my_next_y): # 1/2 の確率ですり抜ける
                        opponent_safe = True
                        opponent_decided_dir = opponent_safer_dir
                    
                    if (opponent_safer_x, opponent_safer_y) == (my_next_x, my_next_y) and len(my_body_deq) == len(opponent_body_deq):
                        my_min_value = 0
        
        """ if depth == 0:
            file = open("debug.txt", "a")
            file.write(str(my_value_list) + '\n')
            file.write(str(opponent_value_list) + '\n')
            file.close() """
        
        if opponent_decided_dir == -1 and not opponent_safe and my_min_value > 0:
            
            """ file = open("debug.txt", "a")
            file.write("勝ち確定？（300行目の分岐）" + '\n')
            file.write("option: ")
            file.write(str(option) + '\n')
            for row in snakes_body_state:
                line = ' '.join(map(str, row))  # 数字をスペース区切りの文字列に変換
                file.write(line + '\n')
            
            file.close() """
            
            deque_one_move_behind(my_body_deq, my_tail_x, my_tail_y, my_get_food, my_will_get_food, foods_place, depth)
            
            my_value_prod_list[first_dir_arg] = INF
            
            continue
        
        """ if depth == 0: # debug
            file = open("debug.txt", "a")
            file.write("decided!!")
            file.write("向き（自分、敵）: ")
            file.write(str(my_next_dir) + " ")
            file.write(str(opponent_decided_dir) + '\n')
            for row in snakes_body_state:
                line = ' '.join(map(str, row))  # 数字をスペース区切りの文字列に変換
                file.write(line + '\n')
            file.close() """
        
        ############################## これ以上探索する必要がないため、打ち切る
        if my_min_value == 0:
            
            # 自蛇の deque を元に戻す
            deque_one_move_behind(my_body_deq, my_tail_x, my_tail_y, my_get_food, my_will_get_food, foods_place, depth)
            
            continue
        
        if my_value_list.count(my_min_value) > 1 and opponent_most_expand_dir != -1: # 敵蛇にとって、自蛇の支配領域を最小化する方向が 2 通り以上あるとき
            opponent_decided_dir = opponent_most_expand_dir
        
        # 自蛇の snakes_body_state を一手先の状態に更新
        body_state_one_move_ahead(snakes_body_state, my_head_x, my_head_y, my_tail_x, my_tail_y, my_body_deq, my_get_food, option)
        
        # 敵の確定させた進行方向に合わせて、deque, snaked_body_state を更新する
        
        # 確定した、敵蛇の次の移動先
        opponent_next_x, opponent_next_y = \
            opponent_head_x + utils.dx[opponent_decided_dir], opponent_head_y + utils.dy[opponent_decided_dir]
        
        opponent_will_get_food, opponent_tail_x, opponent_tail_y = deque_one_move_ahead(opponent_body_deq, opponent_get_food, foods_place, opponent_next_x, opponent_next_y, depth)
        """ file = open("debug.txt", "a")
        file.write(str(opponent_safe) + '\n')
        file.write(str(my_min_value) + '\n')
        file.write(str(opponent_decided_dir) + '\n')
        file.close() """
        body_state_one_move_ahead(snakes_body_state, opponent_head_x, opponent_head_y, opponent_tail_x, opponent_tail_y, opponent_body_deq, opponent_get_food, 1 - option)
        
        ############################## 確定した次の状態 ###############################
        
        # （暫定的な）体の長さで有利であるかどうかのフラグ
        my_next_length_advantage: bool = (len(my_body_deq) > len(opponent_body_deq)) # for debug
        
        my_next_bfs, _ = grid.BFS(my_next_x, my_next_y, my_body_deq, opponent_body_deq, my_will_get_food, opponent_will_get_food) # for debug
        opponent_next_bfs, _ = grid.BFS(opponent_next_x, opponent_next_y, opponent_body_deq, my_body_deq, opponent_will_get_food, my_will_get_food) # for debug
        # 現在の支配領域を加算
        my_value = grid.calc_dominant_space(my_next_bfs, opponent_next_bfs, my_next_x, my_next_y, my_next_length_advantage, depth, 0, -1, -1) # for debug
        
        precalc_dominant_space( # 再帰
                                snakes_body_state,
                                foods_place,
                                my_body_deq,
                                opponent_body_deq,
                                my_will_get_food,
                                opponent_will_get_food,
                                my_next_dir,
                                opponent_decided_dir,
                                my_min_value,
                                my_value_prod_list,
                                depth + 1,
                                fin_depth,
                                first_dir_arg,
                                option,
                                )
        
        ##############################################################################
        
        # 敵蛇の deque、snakes_body_state を元に戻す
        body_state_one_move_behind(snakes_body_state, opponent_head_x, opponent_head_y, opponent_tail_x, opponent_tail_y, opponent_body_deq, opponent_get_food, 1 - option)
        deque_one_move_behind(opponent_body_deq, opponent_tail_x, opponent_tail_y, opponent_get_food, opponent_will_get_food, foods_place, depth)
        
        # 自蛇の deque, snakes_body_state を元に戻す
        body_state_one_move_behind(snakes_body_state, my_head_x, my_head_y, my_tail_x, my_tail_y, my_body_deq, my_get_food, option)
        deque_one_move_behind(my_body_deq, my_tail_x, my_tail_y, my_get_food, my_will_get_food, foods_place, depth)