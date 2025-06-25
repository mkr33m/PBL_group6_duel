INF: int = 2 ** 20

# 盤面サイズ
N: int = 11
# 右 -> 上 -> 左 -> 下
dx = [1, 0, -1, 0]
dy = [0, 1, 0, -1]
direction = ["right", "up", "left", "down"]

# @brief 座標 (x, y) が、グリッドの範囲外にあるかどうかを判定する。
def out_of_grid(x: int, y:int) -> bool:
    if x < 0 or y < 0 or x >= N or y >= N:
        return True
    return False

# @brief 座標 (x1, y1) と座標 (x2, y2) のマンハッタン距離（|x1 - x2| + |y1 - y2|）を返す。
def calc_dist(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x1 - x2) + abs(y1 - y2)

# @brief (x1, y1) -> (y2, y2) はどの方向を数字で返す。
# @remark (x1, y1) と (x2, y2) は隣接している必要がある。
def find_direction(x1: int, y1: int, x2: int, y2: int) -> int:
    assert calc_dist(x1, y1, x2, y2) == 1  # 隣接していることを確認
    diff_x, diff_y = x2 - x1, y2 - y1
    if diff_x == 1 and diff_y == 0: # 右
        return 0
    elif diff_x == 0 and diff_y == 1: # 上
        return 1
    elif diff_x == -1 and diff_y == 0: # 左
        return 2
    return 3 # 下