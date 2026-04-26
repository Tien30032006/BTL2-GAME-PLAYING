# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 18:59:30 2021

@author: AZ
"""
import random
import time
import math

def init_board():
    board = [[+1, +1, +1, +1, +1],
             [+1,  0,  0,  0, +1],
             [+1,  0,  0,  0, -1],
             [-1,  0,  0,  0, -1],
             [-1, -1, -1, -1, -1]]
    return board

def copy_board(board):
    new_board = [row[:] for row in board]
    return new_board

def print_board(board):
    # Định nghĩa mã màu ANSI
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

    print("    0 1 2 3 4") # In tọa độ cột
    print("  +----------+")

    for i in range(5):
        # In tọa độ dòng (do code gốc của bạn dùng [4-i] nên tôi in dòng ngược lại để khớp)
        row_idx = 4 - i
        print(f"{row_idx} | ", end="")

        for j in range(5):
            val = board[row_idx][j]
            if val == 1:
                print(f"{RED}X{RESET}", end=' ')
            elif val == -1:
                print(f"{BLUE}O{RESET}", end=' ')
            else:
                print('.', end=' ')
        print("|")
    print("  +----------+\n")

def dict_neighbors():
    dict_n = {}
    for i in range(5):
        for j in range(5):
            temp = []
            if j == 0:
                temp.append((i, j+1))
            if j == 4:
                temp.append((i, j-1))
            if j > 0 and j < 4:
                temp.append((i, j-1))
                temp.append((i, j+1))
            if i == 0:
                temp.append((i+1, j))
            if i == 4:
                temp.append((i-1, j))
            if i > 0 and i < 4:
                temp.append((i-1, j))
                temp.append((i+1, j))
            if i == j:
                if i == 0:
                    temp.append((i+1, j+1))
                elif i == 4:
                    temp.append((i-1, j-1))
                else:
                    temp.append((i-1, j-1))
                    temp.append((i+1, j+1))
                    temp.append((i+1, j-1))
                    temp.append((i-1, j+1))
            elif i+j == 4:
                if i == 0:
                    temp.append((i+1, j-1))
                elif i == 4:
                    temp.append((i-1, j+1))
                else:
                    temp.append((i-1, j-1))
                    temp.append((i+1, j+1))
                    temp.append((i+1, j-1))
                    temp.append((i-1, j+1))
            if i == 0 and j == 2:
                temp.append((i+1, j-1))
                temp.append((i+1, j+1))
            if i == 4 and j == 2:
                temp.append((i-1, j-1))
                temp.append((i-1, j+1))
            if i == 2 and j == 0:
                temp.append((i+1, j+1))
                temp.append((i-1, j+1))
            if i == 2 and j == 4:
                temp.append((i+1, j-1))
                temp.append((i-1, j-1))
            dict_n[(i,j)] = temp
    return dict_n

dict_nei = dict_neighbors()

# for item in dict_nei:
#     print(item, dict_nei[item])


def get_valid_moves(board, player):
    re = []
    for i in range(5):
        for j in range(5):
            if board[i][j] == player:
                start = (i,j)
                nei = dict_nei[start]
                for item in nei:
                    if board[item[0]][item[1]] == 0:
                        re.append((start,item))
    return re

def ngang(board, i , j, enemy):
    ret = []
    if (board[i][j-1] == enemy) and (board[i][j-1] == board[i][j+1]):
        ret.append((i, j-1))
        ret.append((i, j+1))
    #print("ngang")
    return ret

def doc(board, i, j, enemy):
    ret = []
    if (board[i+1][j] == enemy) and (board[i+1][j] == board[i-1][j]):
        ret.append((i+1, j))
        ret.append((i-1, j))
    #print("doc")
    return ret

def cheo_1(board, i, j, enemy):
    ret = []
    if (board[i+1][j-1] == enemy) and (board[i+1][j-1] == board[i-1][j+1]):
        ret.append((i+1, j-1))
        ret.append((i-1, j+1))
    #print("cheo_1")
    return ret

def cheo_2(board, i, j, enemy):
    ret = []
    if (board[i+1][j+1] == enemy) and (board[i+1][j+1] == board[i-1][j-1]):
        ret.append((i+1, j+1))
        ret.append((i-1, j-1))
    #print("cheo_2")
    return ret

def ganh(board, i, j, enemy):
    ret = []
    if (i, j) in [(1, 1), (2, 2), (3, 3), (3, 1), (1, 3)]:
        ret = doc(board, i, j, enemy) + ngang(board, i, j, enemy) + \
                cheo_1(board, i, j, enemy) + cheo_2(board, i, j, enemy)
    if (i, j) in [(2, 1), (2, 3), (1, 2), (3, 2)]:
        ret = doc(board, i, j, enemy) + ngang(board, i, j, enemy)
    if (i, j) in [(0, 1), (0, 2), (0, 3), (4, 1), (4, 2), (4, 3)]:
        ret = ngang(board, i, j, enemy)
    if (i, j) in [(1, 0), (2, 0), (3, 0), (1, 4), (2, 4), (3, 4)]:
        ret = doc(board, i, j, enemy)
    return ret

def tim_lien_thong(i, j, enemy, board):
    ret = [(i,j)]
    candidates = list(dict_nei[(i,j)])
    for item in candidates:
        if board[item[0]][item[1]] == enemy and item not in ret:
            ret.append(item)
            temp = dict_nei[item]
            for k in temp:
                if k not in candidates:
                    candidates.append(k)
    return ret

def thanh_phan_lien_thong(board, enemy):
    lien_thong = []
    for i in range(5):
        for j in range(5):
            add = True
            if board[i][j] == enemy:
                for l_temp in lien_thong:
                    if (i, j) in l_temp:
                        add = False
                if(add):
                    lien_thong.append(tim_lien_thong(i, j, enemy, board))
    return lien_thong

def tim_khi(tplt, board):
    tap_khi = dict()
    for i in range(len(tplt)):
        item_set = tplt[i]
        temp = []
        for item in item_set:
            neighbors = dict_nei[item]
            for nei in neighbors:
                if nei not in temp and board[nei[0]][nei[1]] == 0:
                    temp.append(nei)
        tap_khi[i] = len(temp)
    return tap_khi


def chet(board, enemy):
    player = -1*enemy
    tplt = thanh_phan_lien_thong(board, enemy)
    khi = tim_khi(tplt, board)
    ret = False # khong chet duoc
    for i in range(len(khi)):
        if khi[i] == 0:
            ret = True
            for (i, j) in tplt[i]:
                board[i][j] = player
    return ret

def act_moves(move, player, board):
    start = move[0]
    end = move[1]

    board[start[0]][start[1]] = 0
    board[end[0]][end[1]] = player
    # ganh
    list_ganh = ganh(board, end[0], end[1], player*-1)
    for item in list_ganh:
        board[item[0]][item[1]] = player
    # chet
    ret2 = chet(board, player*-1)
    # mo
    mo = []
    if len(list_ganh) == 0 and not ret2:
        list_nei = dict_nei[start]
        for item in list_nei:
            if board[item[0]][item[1]] == -1 * player:
                board_copy = copy_board(board)
                move_temp = (item, start)
                ret_temp = ganh(board_copy, start[0], start[1], player)
                if len(ret_temp) > 0:
                    mo.append(move_temp)
    return mo

def npc_move(board, player, mo = None):
    moves = get_valid_moves(board, player)
    if len(moves) == 0:
        return None
    if len(mo) > 0:
        for move in moves:
            if move in mo:
                return move
    index_move = random.randint(0, len(moves) - 1)
    chose_move = moves[index_move]
    for item in moves:
        end = item[1]
        board_copy = copy_board(board)
        enemy = player * (-1)
        l_ganh = ganh(board_copy, end[0], end[1], enemy)
        if len(l_ganh) > 0:
            chose_move = item
            return chose_move

        start = item[0]
        end = item[1]
        board_copy = copy_board(board)
        board_copy[start[0]][start[1]] = 0
        board_copy[end[0]][end[1]] = player
        if chet(board_copy, -1*player):
            return item
    return chose_move



def count_X(board):
    count = 0
    for i in range(5):
        for j in range(5):
            if board[i][j] == 1:
                count = count + 1
    return count

class MCTSNode:
    def __init__(self, board, player_just_moved, parent=None, move=None):
        self.board = board
        self.player_just_moved = player_just_moved
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0.0
        self.visits = 0
        self.player_to_move = self.player_just_moved * -1
        # Sinh untried_moves (chỉ sinh 1 lần để tối ưu)
        self.untried_moves = get_valid_moves(self.board, self.player_to_move)

    def UCT_select_child(self):
        # Hệ số C = 1.414 theo chuẩn MCTS
        log_visits = math.log(self.visits)
        best_child = max(self.children, key=lambda c: (c.wins / c.visits) + 1.414 * math.sqrt(log_visits / c.visits))
        return best_child

    def add_child(self, move):
        new_board = copy_board(self.board)
        act_moves(move, self.player_to_move, new_board)
        child_node = MCTSNode(board=new_board, player_just_moved=self.player_to_move, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(child_node)
        return child_node

def simulate_random_game(board, current_player, original_player):
    temp_board = copy_board(board)
    player_to_move = current_player
    depth = 0
    max_depth = 12
    mo_sim = []

    while depth < max_depth:
        if len(mo_sim) > 0:
            chosen_move = mo_sim[0]
        else:
            moves = get_valid_moves(temp_board, player_to_move)
            if not moves: break
            chosen_move = random.choice(moves)
            
        mo_sim = act_moves(chosen_move, player_to_move, temp_board)
        
        # Early exit nếu có người hết quân
        x_count = count_X(temp_board)
        if x_count == 16 or x_count == 0: break
            
        player_to_move *= -1
        depth += 1

    # Heuristic đánh giá bàn cờ
    my_pieces = 0
    enemy_pieces = 0
    center_control = 0

    for i in range(5):
        for j in range(5):
            val = temp_board[i][j]
            if val == original_player:
                my_pieces += 1
                if i == 2 and j == 2: center_control += 1 # Ưu tiên kiểm soát tâm
            elif val == original_player * -1:
                enemy_pieces += 1
                if i == 2 and j == 2: center_control -= 1

    if enemy_pieces == 0: return 1.0
    if my_pieces == 0: return 0.0

    # Tính điểm
    score = (my_pieces - enemy_pieces) + (center_control * 0.5)

    # Dùng Sigmoid để chuẩn hóa score về dải [0, 1]
    try:
        reward = 1.0 / (1.0 + math.exp(-score * 0.3))
    except OverflowError:
        reward = 1.0 if score > 0 else 0.0

    return reward

def move(board, player, remain_time, mo=None):
    if mo is not None and len(mo) > 0:
        return mo[0]

    start_time = time.time()
    # Nếu remain_time nhỏ hơn 2.8s thì dùng thời gian còn lại, nếu không dùng mức an toàn 2.85s
    time_limit = min(2.85, remain_time - 0.1) if remain_time > 0 else 2.85

    valid_moves = get_valid_moves(board, player)
    if not valid_moves: return None
    if len(valid_moves) == 1: return valid_moves[0]

    # Kiểm tra xem có nước nào đi xong là thắng ngay không
    for m in valid_moves:
        temp_b = copy_board(board)
        act_moves(m, player, temp_b)
        c_x = count_X(temp_b)
        if (player == 1 and c_x == 16) or (player == -1 and c_x == 0):
            print("[CRIT] Đã tìm thấy nước đi kết liễu!")
            return m

    root = MCTSNode(board=board, player_just_moved=player * -1)
    iterations = 0

    while True:
        # Tối ưu tốc độ: Cứ 50 iterations mới check time một lần để tránh overhead
        if iterations % 50 == 0:
            if (time.time() - start_time) >= time_limit:
                break

        node = root
        # Selection
        while len(node.untried_moves) == 0 and len(node.children) > 0:
            node = node.UCT_select_child()

        # Expansion
        if len(node.untried_moves) > 0:
            m = random.choice(node.untried_moves)
            node = node.add_child(m)

        # Simulation
        result = simulate_random_game(node.board, node.player_to_move, original_player=player)

        # Backpropagation
        temp_node = node
        while temp_node is not None:
            if temp_node.player_just_moved == player:
                temp_node.wins += result
            else:
                temp_node.wins += (1.0 - result)
            temp_node.visits += 1
            temp_node = temp_node.parent
            
        iterations += 1

    if len(root.children) == 0:
        return random.choice(valid_moves)

    # Chọn nước đi được khảo sát nhiều nhất (Robust Child)
    best_child = max(root.children, key=lambda c: c.visits)
    print(f"[MCTS] Vòng lặp: {iterations} | Đã chọn: {best_child.move}")
    return best_child.move

def main2(first = 'X'):
    board = init_board()
    count = 0
    limit = 100
    if first == 'X':
        player = 1
    else:
        player = -1
    mo = []
    while(True):
        count = count + 1
        print(count)
        print_board(board)
        if(count > limit):
            X_pieces = count_X(board)
            if X_pieces > 8:
                return 1
            elif X_pieces < 8:
                print("So nuoc di ca van vuot 100, va so quan co cua ban < 8")
                return -1
            else:
                print("So nuoc di ca van vuot 100, va so quan co cua ban = 8")
                return 0
        #b_copy = copy_board(board)
        if player == -1:
            t = time.time()
            chose_move = npc_move(board, player, mo)
            e = time.time() - t
            print(f"⌛ [Quân O - Random] Thời gian suy nghĩ: {e:.4f} giây")
        else:
            t = time.time()
            #chose_move = move(b_copy, player)
            chose_move = move(board, player, 99, mo)
            e = time.time() - t
            print(f"⏳ [Quân X - MCTS] Thời gian suy nghĩ: {e:.4f} giây")

            if e > 3.0:
                print("Thời gian xử lý vượt 3.2 giây")
                return -1
        if chose_move == None:
            if player == 1:
                print("Khong chon duoc nuoc di")
                return -1
            else:
                return 1
        if player == 1 or player == -1:
            if len(mo) > 0:
                # print(mo)
                if chose_move not in mo:
                    print("Nuoc di mo: ", mo)
                    print("Lua chon cua ban: ", chose_move, " sai")
                    return -1
            valid_moves = get_valid_moves(board, player)
            if chose_move not in valid_moves:
                print("Cac nuoc di hop le: ", valid_moves)
                print("Lua chon cua ban: ", chose_move, " sai")
                return -1
        mo = act_moves(chose_move, player, board)
        player = player * -1

    return 0




def test():
    b = init_board()
    print_board(b)
    b[2][2] = 1

    print_board(b)

    move = ((3, 3), (3, 2))
    ret = act_moves(move, -1, b)
    b[3][1] = 1
    print_board(b)
    print(ret)
    move = ((2, 2), (3, 3))
    ret = act_moves(move, 1, b)
    print_board(b)
    print(ret)





#print(main2())


