import time
import random
from collections import deque
from a2_260408 import get_valid_moves, act_moves, copy_board, dict_nei

# ─────────────────────────────────────────────────────────────────
# 1. CONSTANTS & HYPERPARAMETERS
# ─────────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────
# 2. CORE UTILITIES (BFS & Threat Proxy)
# ─────────────────────────────────────────────────────────────────
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
    """Ước lượng O(1) mức độ đe dọa để Move Ordering (Không dùng BFS)."""
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

# ─────────────────────────────────────────────────────────────────
# 3. EVALUATION (Closure với Cache riêng cho mỗi turn)
# ─────────────────────────────────────────────────────────────────
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
                # Bây giờ nó đã hiểu board là gì
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

# ─────────────────────────────────────────────────────────────────
# 4. MOVE ORDERING
# ─────────────────────────────────────────────────────────────────
def _order_moves(board, player, moves, tt_hint, ply_killers):
    def priority(m):
        if m == tt_hint:     return 100_000
        if m in ply_killers: return  90_000
        thr = _quick_threat(board, m, player)
        if thr > 0:          return  50_000 + thr * 1_000
        return POSITION_WEIGHTS[m[1][0]][m[1][1]]

    moves.sort(key=priority, reverse=True)
    return moves

# ─────────────────────────────────────────────────────────────────
# 5. MAIN AGENT ENGINE
# ─────────────────────────────────────────────────────────────────
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
                nmo = act_moves(m, curr_pl, bc)
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
                nmo = act_moves(m, curr_pl, bc)
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
            _, best = minimax(board, d, -INF, INF, True, player, [])
            if best is not None:
                global_best = best
    except TimeoutException:
        pass

    return global_best