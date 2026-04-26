# -*- coding: utf-8 -*-
import pygame
import time
import sys

# Import environment and AI
import MCTS
from a2_260408 import init_board, act_moves, get_valid_moves, count_X, npc_move
import my_agent
import test_agent

# --- UI CONFIGURATION ---
BOARD_SIZE = 600
UI_WIDTH = 300
WIDTH = BOARD_SIZE + UI_WIDTH
HEIGHT = 600
MARGIN = 80
CELL_SIZE = (BOARD_SIZE - 2 * MARGIN) // 4

# Color palette
BG_COLOR = (245, 222, 179)      # Board background
UI_BG = (40, 44, 52)            # Control panel background (Dark mode)
TEXT_COLOR = (255, 255, 255)
LINE_COLOR = (139, 69, 19)
P1_COLOR = (220, 20, 60)        # Red (Player 1)
P2_COLOR = (30, 144, 255)       # Blue (Player -1)
HL_START = (255, 215, 0)
HL_END = (50, 205, 50)
BTN_COLOR = (70, 130, 180)      # Steel blue for buttons
BTN_HOVER = (100, 149, 237)

def copy_board(board):
    return [row[:] for row in board]

def draw_board(screen, board, last_move=None):
    # Draw the left board area
    pygame.draw.rect(screen, BG_COLOR, (0, 0, BOARD_SIZE, HEIGHT))
    
    # Draw lines
    for i in range(5):
        pygame.draw.line(screen, LINE_COLOR, (MARGIN, MARGIN + i * CELL_SIZE), (BOARD_SIZE - MARGIN, MARGIN + i * CELL_SIZE), 3)
        pygame.draw.line(screen, LINE_COLOR, (MARGIN + i * CELL_SIZE, MARGIN), (MARGIN + i * CELL_SIZE, HEIGHT - MARGIN), 3)
        
    for i in range(5):
        for j in range(5):
            if (i + j) % 2 == 0:
                x, y = MARGIN + j * CELL_SIZE, MARGIN + i * CELL_SIZE
                if i < 4 and j < 4:
                    pygame.draw.line(screen, LINE_COLOR, (x, y), (x + CELL_SIZE, y + CELL_SIZE), 3)
                if i > 0 and j < 4:
                    pygame.draw.line(screen, LINE_COLOR, (x, y), (x + CELL_SIZE, y - CELL_SIZE), 3)

    # Highlight the move
    if last_move:
        start, end = last_move
        pygame.draw.circle(screen, HL_START, (MARGIN + start[1] * CELL_SIZE, MARGIN + start[0] * CELL_SIZE), 30, 6)
        pygame.draw.circle(screen, HL_END, (MARGIN + end[1] * CELL_SIZE, MARGIN + end[0] * CELL_SIZE), 38, 6)

    # Draw the pieces
    for i in range(5):
        for j in range(5):
            x = MARGIN + j * CELL_SIZE
            y = MARGIN + i * CELL_SIZE
            if board[i][j] == 1:
                pygame.draw.circle(screen, P1_COLOR, (x, y), 25)
            elif board[i][j] == -1:
                pygame.draw.circle(screen, P2_COLOR, (x, y), 25)

def draw_ui(screen, font, p1_name, p2_name, time1, time2, p1_pieces, p2_pieces, turn, is_paused, match_ended=False, winner_message=""):
    # Draw right panel background
    pygame.draw.rect(screen, UI_BG, (BOARD_SIZE, 0, UI_WIDTH, HEIGHT))
    pygame.draw.line(screen, (200, 200, 200), (BOARD_SIZE, 0), (BOARD_SIZE, HEIGHT), 2)
    
    # Title
    title = font.render("MATCH STATISTICS", True, (255, 215, 0))
    screen.blit(title, (BOARD_SIZE + 20, 20))
    
    # Current turn
    turn_text = font.render(f"Turn: {turn}", True, TEXT_COLOR)
    screen.blit(turn_text, (BOARD_SIZE + 20, 60))

    # Player 1 Info (Red)
    pygame.draw.rect(screen, P1_COLOR, (BOARD_SIZE + 20, 100, 260, 100), border_radius=10)
    screen.blit(font.render(f"🔴 {p1_name} (X)", True, TEXT_COLOR), (BOARD_SIZE + 30, 110))
    screen.blit(font.render(f"Time: {time1:.2f}s", True, TEXT_COLOR), (BOARD_SIZE + 30, 140))
    screen.blit(font.render(f"Pieces: {p1_pieces}", True, TEXT_COLOR), (BOARD_SIZE + 30, 170))

    # Player 2 Info (Blue)
    pygame.draw.rect(screen, P2_COLOR, (BOARD_SIZE + 20, 220, 260, 100), border_radius=10)
    screen.blit(font.render(f"🔵 {p2_name} (O)", True, TEXT_COLOR), (BOARD_SIZE + 30, 230))
    screen.blit(font.render(f"Time: {time2:.2f}s", True, TEXT_COLOR), (BOARD_SIZE + 30, 260))
    screen.blit(font.render(f"Pieces: {p2_pieces}", True, TEXT_COLOR), (BOARD_SIZE + 30, 290))

    # Trạng thái trận đấu
    if match_ended:
        status_text = "MATCH ENDED!"
        status_color = (255, 50, 50)
    else:
        status_text = "PAUSED (REPLAY)" if is_paused else "MATCH IN PROGRESS..."
        status_color = (255, 100, 100) if is_paused else (100, 255, 100)
    
    screen.blit(font.render(status_text, True, status_color), (BOARD_SIZE + 20, 345))

    # Hiển thị người chiến thắng
    if match_ended and winner_message:
        win_surf = font.render(winner_message, True, (255, 215, 0)) 
        screen.blit(win_surf, (BOARD_SIZE + 20, 380))

def draw_buttons(screen, font, mouse_pos):
    # Define coordinates for 3 buttons
    btn_prev = pygame.Rect(BOARD_SIZE + 20, 420, 70, 40)
    btn_pause = pygame.Rect(BOARD_SIZE + 105, 420, 90, 40)
    btn_next = pygame.Rect(BOARD_SIZE + 210, 420, 70, 40)
    
    buttons = [(btn_prev, "< Prev"), (btn_pause, "Pause/Play"), (btn_next, "Next >")]
    
    for rect, text in buttons:
        color = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=5)
        text_surf = font.render(text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
        
    return btn_prev, btn_pause, btn_next

def run_gui_match(agent_1_func, agent_2_func, p1_name, p2_name):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Co Ganh - Replay Tool")
    font = pygame.font.SysFont("Arial", 20, bold=True)
    
    # Initial state
    current_player = 1
    times = {1: 99.0, -1: 99.0}
    mo_list = []
    
    # MATCH HISTORY
    history = [{
        "board": init_board(),
        "move": None,
        "time1": 99.0,
        "time2": 99.0,
        "turn": 0
    }]
    
    view_index = 0
    is_paused = False
    match_ended = False
    winner_message = "" 

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        board_state = history[view_index]
        board = board_state["board"]
        
        # Draw everything
        draw_board(screen, board, board_state["move"])
        x_count, o_count = count_X(board), 16 - count_X(board)
        
        draw_ui(screen, font, p1_name, p2_name, board_state["time1"], board_state["time2"], 
                x_count, o_count, board_state["turn"], is_paused, match_ended, winner_message)
        
        btn_prev, btn_pause, btn_next = draw_buttons(screen, font, mouse_pos)
        
        pygame.display.flip()

        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_prev.collidepoint(event.pos):
                    is_paused = True 
                    view_index = max(0, view_index - 1)
                elif btn_next.collidepoint(event.pos):
                    is_paused = True
                    view_index = min(len(history) - 1, view_index + 1)
                elif btn_pause.collidepoint(event.pos):
                    if not match_ended:
                        is_paused = not is_paused
                        if not is_paused:
                            view_index = len(history) - 1

        # GAME PLAYING PROCESSING
        if not is_paused and not match_ended and view_index == len(history) - 1:
            turn_count = len(history)
            x_count, o_count = count_X(board), 16 - count_X(board)

            # Điều kiện 1 - Bị ăn hết quân
            if x_count == 0:
                match_ended = True
                winner_message = f"WINNER: {p2_name}!"
                continue
            elif o_count == 0:
                match_ended = True
                winner_message = f"WINNER: {p1_name}!"
                continue

            # Điều kiện 2 - Vượt quá 100 lượt
            if turn_count > 100:
                match_ended = True
                if x_count > o_count:
                    winner_message = f"{p1_name} WINS (Score)!"
                elif o_count > x_count:
                    winner_message = f"{p2_name} WINS (Score)!"
                else:
                    winner_message = "DRAW!"
                continue

            # Lấy danh sách nước đi hợp lệ để kiểm tra
            valid_moves = get_valid_moves(board, current_player)
            
            # Điều kiện 3 - Hết nước đi hợp lệ
            if not valid_moves:
                match_ended = True
                winner = p2_name if current_player == 1 else p1_name
                winner_message = f"{winner} WINS (No moves)!"
                continue

            # =================================================================
            # LẤY NƯỚC ĐI TỪ AI VÀ XỬ LÝ LINH HOẠT THAM SỐ
            # =================================================================
            start_time = time.time()
            agent_func = agent_1_func if current_player == 1 else agent_2_func
            curr_name = p1_name if current_player == 1 else p2_name
            player_char = 'X' if current_player == 1 else 'O'

            try:
                # Cố gắng truyền tham số mo_list (Cho MCTS hoặc các hàm có 4 tham số)
                move = agent_func(board, current_player, times[current_player], mo_list)
            except TypeError:
                # Nếu hàm AI chỉ có 3 tham số (Như my_agent.move), bỏ qua mo_list
                move = agent_func(board, current_player, times[current_player])
            
            # 🛡️ LỚP BẢO HỘ TRỌNG TÀI: Ép luật Mở (Bắt buộc Gánh)
            # Dù AI tính toán ra nước nào, nếu có luật Mở mà AI không đi đúng, GUI sẽ tự sửa.
            if mo_list and move not in mo_list:
                print(f"[*] HỖ TRỢ TRỌNG TÀI: {curr_name} chọn {move} vi phạm luật Mở (Bắt buộc Gánh).")
                print(f"    -> Tự động sửa nước đi thành: {mo_list[0]}")
                move = mo_list[0]

            time_taken = time.time() - start_time
            times[current_player] -= time_taken
            
            # --- LOG RA CONSOLE ---
            print(f"[Quân {player_char} - {curr_name}] Thời gian suy nghĩ: {time_taken:.4f}s | Quỹ thời gian còn: {times[current_player]:.2f}s")
            print(f"-> {curr_name} chọn nước đi: {move}")

            # --- KIỂM TRA ĐI SAI LUẬT CHUNG ---
            if move not in valid_moves:
                print(f"Lựa chọn của bạn:  {move}  sai luật (Không nằm trong valid_moves).")
                match_ended = True
                winner = p2_name if current_player == 1 else p1_name
                winner_message = f"{winner} WINS (Illegal Move)!"
                continue

            # Điều kiện 4 - Hết giờ / Quá thời gian quy định cho 1 lượt
            if times[current_player] <= 0 or time_taken > 3.2:
                print(f"Player {current_player} timed out or ran out of time!")
                match_ended = True
                winner = p2_name if current_player == 1 else p1_name
                winner_message = f"{winner} WINS (Timeout)!"
                continue

            # Thực thi nước đi và lấy danh sách bắt buộc gánh cho lượt sau
            new_board = copy_board(board)
            mo_list = act_moves(move, current_player, new_board)
            
            history.append({
                "board": new_board,
                "move": move,
                "time1": times[1],
                "time2": times[-1],
                "turn": turn_count
            })
            view_index += 1
            current_player *= -1
            
            # Delay 0.5s so human eyes can catch the auto move
            pygame.time.delay(500)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    print("Opening analysis interface...")
    run_gui_match(my_agent.move, MCTS.move, p1_name="My AI", p2_name="Opponent AI")