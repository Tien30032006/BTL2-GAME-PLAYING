import time
from a2_260408 import init_board, act_moves, get_valid_moves, count_X, npc_move
import my_agent
import test_agent
import MCTS


# --- CẤU HÌNH TEST ---
TOTAL_MATCHES = 10
TIME_LIMIT_TOTAL = 99.0
TIME_LIMIT_PER_MOVE = 3.0
MAX_TURNS = 100  # Giới hạn số lượt tối đa

def random_agent_wrapper(board, player, remain_time):
    """Wrapper để tương thích hàm npc_move của thầy với format có remain_time"""
    return npc_move(board, player, [])

def run_single_match(agent_1_func, agent_2_func):
    """Chạy 1 trận đấu không giao diện và trả về kết quả thống kê"""
    board = init_board()
    times = {1: TIME_LIMIT_TOTAL, -1: TIME_LIMIT_TOTAL}
    time_used = {1: 0.0, -1: 0.0}
    current_player = 1
    mo_list = []
    turn_count = 0
    
    while True:
        # =========================================================
        # 1. KIỂM TRA GIỚI HẠN 100 LƯỢT
        # =========================================================
        if turn_count >= MAX_TURNS:
            x_count = count_X(board)
            o_count = 16 - x_count
            if x_count > o_count:
                return 1, turn_count, time_used[1], time_used[-1], f"Hết 100 lượt (X thắng {x_count}-{o_count})"
            elif o_count > x_count:
                return -1, turn_count, time_used[1], time_used[-1], f"Hết 100 lượt (O thắng {o_count}-{x_count})"
            else:
                return 0, turn_count, time_used[1], time_used[-1], "Hết 100 lượt (Hòa)"

        valid_moves = get_valid_moves(board, current_player)
        
        # Thua do hết nước đi
        if not valid_moves:
            return -current_player, turn_count, time_used[1], time_used[-1], "Hết nước đi"
            
        start_time = time.time()
        
        # =========================================================
        # 2. GỌI AI SUY NGHĨ (TRUYỀN THÊM MO_LIST CHO ĐỐI THỦ)
        # =========================================================
        if current_player == 1:
            # My AI (X) tự tracking ngầm nên chỉ cần 3 tham số
            move = agent_1_func(board, current_player, times[1])
        else:
            # Truyền mo_list cho MCTS (O)
            try:
                # Thử truyền tham số thứ 4 nếu MCTS.move đã hỗ trợ
                move = agent_2_func(board, current_player, times[-1], mo_list)
            except TypeError:
                # Nếu MCTS.move chỉ nhận 3 tham số (chưa sửa), gọi theo kiểu cũ
                move = agent_2_func(board, current_player, times[-1])
                
        time_taken = time.time() - start_time
        times[current_player] -= time_taken
        time_used[current_player] += time_taken
        
        # =========================================================
        # KIỂM TRA TÍNH HỢP LỆ VÀ LUẬT MỞ (BẮT BUỘC GÁNH)
        # =========================================================
        # 1. Kiểm tra luật bắt buộc gánh
        if mo_list and move not in mo_list:
            reason = f"Vi phạm luật Mở (Đi {move}, bắt buộc {mo_list})"
            return -current_player, turn_count, time_used[1], time_used[-1], reason
            
        # 2. Kiểm tra nước đi có hợp lệ cơ bản không (đề phòng đi bậy)
        if move not in valid_moves:
            reason = f"Nước đi sai luật (Không nằm trong valid_moves)"
            return -current_player, turn_count, time_used[1], time_used[-1], reason
        # =========================================================
        
        # =========================================================
        # KIỂM TRA TÍNH HỢP LỆ VÀ LUẬT MỞ (BẮT BUỘC GÁNH)
        # =========================================================
        if mo_list and move not in mo_list:
            reason = f"Vi phạm luật Mở (Đi {move}, bắt buộc {mo_list})"
            return -current_player, turn_count, time_used[1], time_used[-1], reason
            
        if move not in valid_moves:
            reason = f"Nước đi sai luật (Không nằm trong valid_moves)"
            return -current_player, turn_count, time_used[1], time_used[-1], reason
        
        # Xử thua do vi phạm thời gian
        if time_taken > TIME_LIMIT_PER_MOVE:
            return -current_player, turn_count, time_used[1], time_used[-1], f"Timeout ({time_taken:.2f}s/move)"
        if times[current_player] <= 0:
            return -current_player, turn_count, time_used[1], time_used[-1], "Hết tổng 99s"
            
        # Cập nhật bàn cờ và lấy danh sách "Mở" cho đối thủ ở lượt kế tiếp
        mo_list = act_moves(move, current_player, board)
        turn_count += 1
        current_player *= -1
        
        # Kiểm tra xem có bên nào hết sạch quân chưa (Fast check)
        x_count = count_X(board)
        if x_count == 0:
            return -1, turn_count, time_used[1], time_used[-1], "Bị quét sạch quân"
        elif x_count == 16:
            return 1, turn_count, time_used[1], time_used[-1], "Bị quét sạch quân"

if __name__ == "__main__":
    print(f"BẮT ĐẦU CHẠY THỬ NGHIỆM {TOTAL_MATCHES} TRẬN")
    print("-" * 80)
    print(f"{'Trận':<6} | {'Người Thắng':<15} | {'Lượt':<6} | {'Thời gian AI (X)':<20} | {'Lý do'}")
    print("-" * 80)
    
    stats = {
        "AI_win": 0,
        "Random_win": 0,
        "Draw": 0,
        "Total_turns": 0,
        "Total_AI_time": 0.0
    }
    
    for i in range(1, TOTAL_MATCHES + 1):
        # AI của bạn cầm quân X (1), MCTS cầm quân O (-1)
        winner, turns, ai_time, random_time, reason = run_single_match(my_agent.move, MCTS.move)
        
        stats["Total_turns"] += turns
        stats["Total_AI_time"] += ai_time
        
        if winner == 1:
            stats["AI_win"] += 1
            win_str = "My AI (X)"
        elif winner == -1:
            stats["Random_win"] += 1
            win_str = "MCTS (O)"
        else:
            stats["Draw"] += 1
            win_str = "HÒA"
            
        print(f"#{i:<4} | {win_str:<15} | {turns:<5} | {ai_time:<14.3f} | {random_time:<14.3f} | {reason}")

    # --- TỔNG KẾT ---
    print("=" * 80)
    print("BÁO CÁO THỐNG KÊ SAU", TOTAL_MATCHES, "TRẬN")
    print("=" * 80)
    
    ai_win_rate = (stats["AI_win"] / TOTAL_MATCHES) * 100
    avg_turns = stats["Total_turns"] / TOTAL_MATCHES
    avg_time_per_match = stats["Total_AI_time"] / TOTAL_MATCHES
    
    print(f"* Tỷ lệ thắng của My AI : {ai_win_rate:.1f}% ({stats['AI_win']} Thắng - {stats['Draw']} Hòa - {stats['Random_win']} Thua)")
    print(f"* Trung bình số nước đi  : {avg_turns:.1f} nước / trận")
    print(f"* Trung bình tiêu hao thời gian (My AI) : {avg_time_per_match:.2f} giây / trận")
    print("=" * 80)