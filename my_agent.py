import time
import random
from collections import deque

# =================================================================
# PHẦN 1: CORE ENGINE (Bóc tách trực tiếp từ a2_260408.py)
# =================================================================

def copy_board(board):
    return [row[:] for row in board]

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
    return ret

def doc(board, i, j, enemy):
    ret = []
    if (board[i+1][j] == enemy) and (board[i+1][j] == board[i-1][j]):
        ret.append((i+1, j))
        ret.append((i-1, j))
    return ret

def cheo_1(board, i, j, enemy):
    ret = []
    if (board[i+1][j-1] == enemy) and (board[i+1][j-1] == board[i-1][j+1]):
        ret.append((i+1, j-1))
        ret.append((i-1, j+1))
    return ret

def cheo_2(board, i, j, enemy):
    ret = []
    if (board[i+1][j+1] == enemy) and (board[i+1][j+1] == board[i-1][j-1]):
        ret.append((i+1, j+1))
        ret.append((i-1, j-1)) 
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
    ret = False
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

def count_X(board):
    count = 0
    for i in range(5):
        for j in range(5):
            if board[i][j] == 1:
                count += 1
    return count

def print_board(board):
    for i in range(5):
        for j in range(5):
            if board[4-i][j] == 1:
                print('X', end=' ')
            elif board[4-i][j] == -1:
                print('O', end=' ')
            else:
                print('-', end=' ')
        print()
    print()

def init_board():
    board = [[+1, +1, +1, +1, +1],
             [+1,  0,  0,  0, +1],
             [+1,  0,  0,  0, -1],
             [-1,  0,  0,  0, -1],
             [-1, -1, -1, -1, -1]]
    return board

# AI NPC ĐỂ TEST ĐÁNH RANDOM
def npc_move(board, player, mo=None):
    if mo is None:
        mo = []
    moves = get_valid_moves(board, player)
    if len(moves) == 0: return None
    if len(mo) > 0:
        for m in moves:
            if m in mo: return m
            
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

# =================================================================
# PHẦN 2: CONSTANTS & HYPERPARAMETERS CHO AI
# =================================================================

POSITION_WEIGHTS = [
    [2, 3, 4, 3, 2],
    [3, 4, 5, 4, 3],
    [4, 5, 7, 5, 4],
    [3, 4, 5, 4, 3],
    [2, 3, 4, 3, 2],
]

INF        = float('inf')
MAX_DEPTH  = 12
NODE_CHECK = 512   
LAZY_THRESHOLD = 3 

class TimeoutException(Exception):
    """Exception để ngắt toàn bộ stack đệ quy ngay lập tức khi hết giờ."""
    pass

# =================================================================
# PHẦN 3: CORE UTILITIES CHO AI (BFS & Threat Proxy)
# =================================================================

def _groups_and_liberties(board, p):
    """Trả về list[(frozenset_cells, set_liberties)] của mọi nhóm quân p."""
    visited = set()
    results = []
    for r in range(5):
        for c in range(5):
            if board[r][c] == p and (r, c) not in visited:
                group     = set()
                liberties = set()
                q = deque([(r, c)])
                while q:
                    x, y = q.popleft()
                    if (x, y) in group:
                        continue
                    group.add((x, y))
                    visited.add((x, y))
                    for nx, ny in dict_nei[(x, y)]:
                        cell = board[nx][ny]
                        if cell == 0:
                            liberties.add((nx, ny))
                        elif cell == p and (nx, ny) not in group:
                            q.append((nx, ny))
                results.append((frozenset(group), liberties))
    return results

def _quick_threat(board, move, player):
    """Ước lượng O(1) mức độ đe dọa để Move Ordering."""
    (r0, c0), (r1, c1) = move
    enemy = -player
    
    # In-place move
    board[r0][c0] = 0
    board[r1][c1] = player

    threat = 0
    seen = set()
    for nx, ny in dict_nei[(r1, c1)]:
        if board[nx][ny] != enemy or (nx, ny) in seen:
            continue
        seen.add((nx, ny))
        # Đếm Khí cục bộ (immediate liberties)
        libs = sum(1 for ex, ey in dict_nei[(nx, ny)] if board[ex][ey] == 0)
        if libs == 0:
            threat += 10   # Chắc chắn ăn
        elif libs == 1:
            threat += 4    # Đang ép (Atari)
        elif libs == 2:
            threat += 1    # Tiếp cận

    # Hoàn tác
    board[r0][c0] = player
    board[r1][c1] = 0
    return threat

# =================================================================
# PHẦN 4: EVALUATION & MOVE ORDERING
# =================================================================

def _build_evaluator(player):
    eval_cache: dict = {}

    def _lib_score(board, groups_libs, attacking):
        attacker = player if attacking else -player
        s = 0
        for _grp, liberties in groups_libs:
            n = len(liberties)
            if n == 0:
                s += 3000 if attacking else -3000
            elif n == 1:
                lone = next(iter(liberties))
                real = any(board[nx][ny] == attacker for nx, ny in dict_nei[lone]) 
                bonus = 600 if real else 200
                s += bonus if attacking else -bonus
            elif n == 2:
                s += 80 if attacking else -80
        return s

    def evaluate(board):
        bh = tuple(tuple(row) for row in board)
        if bh in eval_cache:
            return eval_cache[bh]

        p_count = 0
        e_count = 0
        pos_score = 0
        for i in range(5):
            for j in range(5):
                v = board[i][j]
                if v == player:
                    p_count += 1
                    pos_score += POSITION_WEIGHTS[i][j]
                elif v == -player:
                    e_count += 1
                    pos_score -= POSITION_WEIGHTS[i][j]

        if e_count == 0: return 200_000
        if p_count == 0: return -200_000

        score = (p_count - e_count) * 400 + pos_score

        # Lazy BFS: Chỉ phân tích Khí khi thế cờ giằng co
        if abs(p_count - e_count) < LAZY_THRESHOLD:
            score += _lib_score(board, _groups_and_liberties(board, -player), attacking=True)
            score += _lib_score(board, _groups_and_liberties(board,  player), attacking=False)

        eval_cache[bh] = score
        return score

    return evaluate

def _order_moves(board, player, moves, tt_hint, ply_killers):
    def priority(m):
        if m == tt_hint:     return 100_000
        if m in ply_killers: return  90_000
        thr = _quick_threat(board, m, player)
        if thr > 0:          return  50_000 + thr * 1_000
        return POSITION_WEIGHTS[m[1][0]][m[1][1]]

    moves.sort(key=priority, reverse=True)
    return moves

# =================================================================
# PHẦN 5: MAIN AGENT ENGINE (Giao tiếp đúng 3 tham số)
# =================================================================

def move(board, player, remain_time):
    start_time = time.time()

    valid_moves = get_valid_moves(board, player)
    if not valid_moves: return None
    if len(valid_moves) == 1: return valid_moves[0]

    # --- LỚP KHIÊN 1: GLOBAL HISTORY ---
    if not hasattr(move, "global_history"):
        move.global_history = {}
    current_hash = (tuple(tuple(row) for row in board), player)
    move.global_history[current_hash] = move.global_history.get(current_hash, 0) + 1
    state_history = move.global_history.copy()

    # --- QUẢN LÝ THỜI GIAN LINH ĐỘNG ---
    if remain_time > 60:
        time_limit = 2.8
    elif remain_time > 20:
        time_limit = 1.5
    elif remain_time > 8:
        time_limit = 0.8
    else:
        time_limit = 0.3

    evaluate = _build_evaluator(player)
    
    tt: dict = {}
    killers = [[] for _ in range(MAX_DEPTH + 4)]
    node_counter = [0]
    global_best = valid_moves[0]

    def _hash(b, pl):
        return (tuple(tuple(row) for row in b), pl)

    def minimax(b, depth, alpha, beta, is_max, curr_pl, mo_list, ply=0):
        node_counter[0] += 1
        if node_counter[0] & (NODE_CHECK - 1) == 0:
            if time.time() - start_time > time_limit:
                raise TimeoutException()

        h = _hash(b, curr_pl)

        # Anti-loop
        visits = state_history.get(h, 0)
        if visits >= 2:
            return (-8_000 if is_max else 8_000), None

        # TT Lookup
        cached = tt.get(h)
        if cached and cached[0] >= depth:
            _, cs, cf, cm = cached
            if cf == 'EXACT': return cs, cm
            if cf == 'LOWER': alpha = max(alpha, cs)
            elif cf == 'UPPER': beta = min(beta, cs)
            if alpha >= beta: return cs, cm

        if depth == 0:
            return evaluate(b), None

        # Sinh nước đi
        moves = get_valid_moves(b, curr_pl)
        # Bắt buộc gánh nếu nằm trong thế cờ mở
        if mo_list:
            forced = [m for m in moves if m in mo_list]
            if forced: moves = forced
        if not moves:
            return evaluate(b), None

        # --- LỚP KHIÊN 2: SYMMETRY BREAKING ---
        random.shuffle(moves)

        tt_hint     = cached[3] if cached else None
        ply_killers = killers[ply] if ply < len(killers) else []
        moves = _order_moves(b, curr_pl, moves, tt_hint, ply_killers)

        best_move  = moves[0]
        orig_alpha = alpha
        state_history[h] = visits + 1

        if is_max:
            best_val = -INF
            for m in moves:
                bc  = copy_board(b)
                nmo = act_moves(m, curr_pl, bc) # Sinh danh sách bắt buộc cho turn sau
                val, _ = minimax(bc, depth - 1, alpha, beta, False, -curr_pl, nmo, ply + 1)
                if val > best_val:
                    best_val, best_move = val, m
                alpha = max(alpha, val)
                if beta <= alpha:
                    if ply < len(killers) and m not in killers[ply]:
                        killers[ply] = ([m] + killers[ply])[:2]
                    break
        else:
            best_val = INF
            for m in moves:
                bc  = copy_board(b)
                nmo = act_moves(m, curr_pl, bc) # Sinh danh sách bắt buộc cho turn sau
                val, _ = minimax(bc, depth - 1, alpha, beta, True, -curr_pl, nmo, ply + 1)
                if val < best_val:
                    best_val, best_move = val, m
                beta = min(beta, val)
                if beta <= alpha:
                    if ply < len(killers) and m not in killers[ply]:
                        killers[ply] = ([m] + killers[ply])[:2]
                    break

        state_history[h] = visits

        # Lưu TT
        if best_val <= orig_alpha:   flag = 'UPPER'
        elif best_val >= beta:       flag = 'LOWER'
        else:                        flag = 'EXACT'
        tt[h] = (depth, best_val, flag, best_move)

        return best_val, best_move

    # --- ITERATIVE DEEPENING ---
    try:
        for d in range(1, MAX_DEPTH + 1):
            node_counter[0] = 0
            # Root truyền mảng trống vì hàm move không nhận tham số mo
            _, best = minimax(board, d, -INF, INF, True, player, [])
            if best is not None:
                global_best = best
    except TimeoutException:
        pass

    return global_best


# =================================================================
# PHẦN 6: MAIN TEST (MÔ PHỎNG REFEREE CỦA TRƯỜNG)
# =================================================================
if __name__ == "__main__":
    print("=====================================================")
    print(" TRẬN ĐẤU THỬ NGHIỆM: MY AI (Quân X) vs RANDOM (Quân O) ")
    print("=====================================================")
    
    board = init_board()
    current_player = 1  # 1: My AI (X), -1: Random (O)
    turn_count = 0
    limit = 100
    times = {1: 99.0, -1: 99.0}

    print_board(board)

    while True:
        turn_count += 1
        print(f"\n--- Lượt {turn_count} ---")
        
        if turn_count > limit:
            x_count = count_X(board)
            o_count = 16 - x_count
            print(f"Đã đạt giới hạn {limit} lượt!")
            if x_count > o_count:
                print(f"MY AI (X) THẮNG vì có nhiều quân hơn ({x_count} - {o_count})")
            elif o_count > x_count:
                print(f"RANDOM (O) THẮNG vì có nhiều quân hơn ({o_count} - {x_count})")
            else:
                print("TRẬN ĐẤU HÒA!")
            break

        # Gọi AI suy nghĩ theo format chuẩn của referee (Chỉ 3 tham số)
        if current_player == 1:
            print(f"My AI (X) đang suy nghĩ... (Thời gian còn: {times[1]:.2f}s)")
            t = time.time()
            chose_move = move(board, current_player, times[1])
            elapsed = time.time() - t
            times[1] -= elapsed
            print(f"-> Quyết định: {chose_move} (Tốn {elapsed:.4f}s)")
        else:
            print("Random NPC (O) đang đi...")
            # AI Random nội bộ vẫn gọi với cấu trúc hàm cũ của trường
            chose_move = npc_move(board, current_player)
            print(f"-> Quyết định: {chose_move}")

        if chose_move is None:
            winner = "Random NPC (O)" if current_player == 1 else "My AI (X)"
            print(f"Không còn nước đi! {winner} DÀNH CHIẾN THẮNG.")
            break

        # Thực thi nước đi và lấy mo_list (Nhưng không truyền vào lượt sau ở cấp root)
        act_moves(chose_move, current_player, board)
        current_player *= -1
        print_board(board)

        # Kiểm tra điều kiện kết thúc sớm
        x_count = count_X(board)
        if x_count == 16:
            print("MY AI (X) ĐÃ QUÉT SẠCH QUÂN ĐỐI PHƯƠNG! CHIẾN THẮNG.")
            break
        elif x_count == 0:
            print("RANDOM NPC (O) ĐÃ QUÉT SẠCH QUÂN X! CHIẾN THẮNG.")
            break