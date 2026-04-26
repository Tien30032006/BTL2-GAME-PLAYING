# -*- coding: utf-8 -*-
import time
from a2_260408 import (get_valid_moves, act_moves, copy_board,
                        thanh_phan_lien_thong, tim_khi, ganh, dict_nei)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
POSITION_WEIGHTS = [
    [2, 3, 4, 3, 2],
    [3, 4, 5, 4, 3],
    [4, 5, 7, 5, 4],
    [3, 4, 5, 4, 3],
    [2, 3, 4, 3, 2]
]

INF = float('inf')

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def hash_board(board):
    return tuple(tuple(row) for row in board)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def evaluate_board(board, player):
    """
    Heuristic evaluation from `player`'s perspective.
    Returns a score in (-100_000, 100_000).  +-100_000 = forced win/loss.
    """
    p_count = 0
    e_count = 0
    score = 0
    player_pieces = []
    enemy_pieces  = []

    for i in range(5):
        for j in range(5):
            v = board[i][j]
            if v == player:
                p_count += 1
                score += POSITION_WEIGHTS[i][j]
                player_pieces.append((i, j))
            elif v == -player:
                e_count += 1
                score -= POSITION_WEIGHTS[i][j]
                enemy_pieces.append((i, j))

    # Terminal detection
    if e_count == 0: return  100_000
    if p_count == 0: return -100_000

    # 1. Piece-count advantage (dominant factor)
    score += (p_count - e_count) * 2000

    # 2. Liberty (khi) analysis with threat awareness
    def liberty_score(tplt, khi, attacking):
        """
        attacking=True  -> enemy groups we want to suffocate  -> positive score.
        attacking=False -> our own groups we want to keep safe -> negative penalty.
        """
        s = 0
        for idx, so_khi in khi.items():
            group = tplt[idx]
            if so_khi == 0:
                s += 2000 if attacking else -2000
            elif so_khi == 1:
                # Locate the lone liberty cell
                lone_lib = None
                for (r, c) in group:
                    for nb in dict_nei[(r, c)]:
                        if board[nb[0]][nb[1]] == 0:
                            lone_lib = nb
                            break
                    if lone_lib:
                        break
                # Check if an opponent piece is adjacent to that liberty
                bonus = 200
                if lone_lib:
                    attacker_piece = player if attacking else -player
                    if any(board[nb[0]][nb[1]] == attacker_piece
                           for nb in dict_nei[lone_lib]):
                        bonus = 600   # Real, immediate threat
                s += bonus if attacking else -bonus
            else:
                s += (-so_khi * 8) if attacking else (so_khi * 8)
        return s

    tplt_enemy = thanh_phan_lien_thong(board, -player)
    khi_enemy  = tim_khi(tplt_enemy, board)
    score += liberty_score(tplt_enemy, khi_enemy, attacking=True)

    tplt_player = thanh_phan_lien_thong(board, player)
    khi_player  = tim_khi(tplt_player, board)
    score += liberty_score(tplt_player, khi_player, attacking=False)

    # 3. Endgame: chase enemy pieces when clearly winning
    if p_count > e_count + 1 and enemy_pieces:
        for p_r, p_c in player_pieces:
            score -= min(abs(p_r - e_r) + abs(p_c - e_c)
                         for e_r, e_c in enemy_pieces) * 5

    return score


# ---------------------------------------------------------------------------
# Move scoring helper (in-place board modification – no copy overhead)
# ---------------------------------------------------------------------------
def ganh_count(board, m, pl):
    """Return pieces captured by ganh if pl makes move m. Restores board after."""
    sr, sc = m[0]
    er, ec = m[1]
    board[sr][sc] = 0
    board[er][ec] = pl
    n = len(ganh(board, er, ec, -pl))
    board[sr][sc] = pl
    board[er][ec] = 0
    return n


# ---------------------------------------------------------------------------
# Main agent entry point
# ---------------------------------------------------------------------------
def move(board, player, remain_time):
    _start     = time.time()
    _limit     = 2.5         # Hard per-move budget (well below the 3.2 s rule)
    _timed_out = [False]     # Mutable flag: set once, signals the whole search

    def is_out():
        if _timed_out[0]: return True
        if time.time() - _start >= _limit:
            _timed_out[0] = True
            return True
        return False

    valid_moves = get_valid_moves(board, player)
    if not valid_moves: return None
    if len(valid_moves) == 1: return valid_moves[0]

    # -------------------------------------------------------------------
    # Transposition table
    # KEY = (board_hash, active_player)
    # BUG FIX: same board with different active player has a different value.
    # -------------------------------------------------------------------
    tt = {}

    # Killer moves: 2 slots per distance-from-root ply
    MAX_DEPTH = 8
    killers = [[] for _ in range(MAX_DEPTH + 2)]

    # -------------------------------------------------------------------
    # Move ordering
    # -------------------------------------------------------------------
    def move_priority(b, m, pl, hint, ply_killers):
        if m == hint:          return 100_000          # TT best move
        if m in ply_killers:   return  90_000          # Killer move
        n = ganh_count(b, m, pl)
        if n > 0:              return  50_000 + n * 5_000   # Capture
        return POSITION_WEIGHTS[m[1][0]][m[1][1]]      # Positional

    def order_moves(b, pl, mo, hint=None, ply=0):
        vm = get_valid_moves(b, pl)
        if mo:
            forced = [m for m in vm if m in mo]
            if forced: return forced
        pk = killers[ply] if ply < len(killers) else []
        vm.sort(key=lambda m: move_priority(b, m, pl, hint, pk), reverse=True)
        return vm

    # -------------------------------------------------------------------
    # Alpha-beta search
    # -------------------------------------------------------------------
    def ab(b, d, alpha, beta, maxing, pl, mo, ply=0):
        """
        Returns (score, best_move).
        On timeout: _timed_out[0] is True; caller discards the return value.
        """
        if is_out(): return 0, None

        # TT lookup (correct key includes active player)
        h = (hash_board(b), pl)
        cached = tt.get(h)
        if cached and cached[0] >= d:
            _, cs, cf, cm = cached
            if cf == 'E': return cs, cm
            if cf == 'L': alpha = max(alpha, cs)
            elif cf == 'U': beta  = min(beta,  cs)
            if alpha >= beta: return cs, cm

        if d == 0:
            return evaluate_board(b, player), None

        hint  = cached[3] if cached else None
        moves = order_moves(b, pl, mo, hint, ply)
        if not moves: return evaluate_board(b, player), None

        best_val  = -INF if maxing else INF
        best_mv   = moves[0]
        orig_alpha = alpha
        completed  = True

        for m in moves:
            if is_out():
                completed = False
                break

            bc  = copy_board(b)
            nmo = act_moves(m, pl, bc)
            val, _ = ab(bc, d - 1, alpha, beta, not maxing, -pl, nmo, ply + 1)

            # Child timed out -> discard val (may be 0 / stale)
            if _timed_out[0]:
                completed = False
                break

            if maxing:
                if val > best_val:
                    best_val, best_mv = val, m
                alpha = max(alpha, val)
                if beta <= alpha:
                    # Beta cutoff -> register as killer
                    if ply < len(killers) and m not in killers[ply]:
                        killers[ply] = ([m] + killers[ply])[:2]
                    break
            else:
                if val < best_val:
                    best_val, best_mv = val, m
                beta = min(beta, val)
                if beta <= alpha:
                    if ply < len(killers) and m not in killers[ply]:
                        killers[ply] = ([m] + killers[ply])[:2]
                    break

        # Write to TT only when we completed this node fully
        if completed:
            if maxing:
                flag = 'U' if best_val <= orig_alpha else ('L' if best_val >= beta else 'E')
            else:
                flag = 'L' if best_val >= beta else ('U' if best_val <= alpha else 'E')
            tt[h] = (d, best_val, flag, best_mv)

        return best_val, best_mv

    # -------------------------------------------------------------------
    # Iterative deepening
    # -------------------------------------------------------------------
    best = valid_moves[0]   # guaranteed safe fallback

    for d in range(1, MAX_DEPTH + 1):
        if is_out(): break
        _timed_out[0] = False       # reset signal for this iteration

        score, bm = ab(board, d, -INF, INF, True, player, [])

        # Only accept a depth result that was fully searched
        if not _timed_out[0] and bm is not None:
            best = bm

    return best