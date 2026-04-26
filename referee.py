import time
from a2_260408 import init_board, act_moves, get_valid_moves, count_X, npc_move
import my_agent
import test_agent
import MCTS
# --- CẤU HÌNH TEST ---
TOTAL_MATCHES = 10
TIME_LIMIT_TOTAL = 99.0
TIME_LIMIT_PER_MOVE = 3.0

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
    
    # Đã bỏ giới hạn turn, vòng lặp chạy đến khi có kết quả
    while True:
        valid_moves = get_valid_moves(board, current_player)
        
        # Thua do hết nước đi
        if not valid_moves:
            return -current_player, turn_count, time_used[1], time_used[-1], "Hết nước đi"
            
        start_time = time.time()
        
        # Gọi AI suy nghĩ
        if current_player == 1:
            move = agent_1_func(board, current_player, times[1])
        else:
            move = agent_2_func(board, current_player, times[-1])
            
        time_taken = time.time() - start_time
        times[current_player] -= time_taken
        time_used[current_player] += time_taken
        
        # Xử thua do vi phạm thời gian
        if time_taken > TIME_LIMIT_PER_MOVE:
            return -current_player, turn_count, time_used[1], time_used[-1], f"Timeout ({time_taken:.2f}s/move)"
        if times[current_player] <= 0:
            return -current_player, turn_count, time_used[1], time_used[-1], "Hết tổng 99s"
            
        # Cập nhật bàn cờ
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
        # AI của bạn cầm quân X (1), Random Agent cầm quân O (-1)
        winner, turns, ai_time, random_time, reason = run_single_match(my_agent.move, MCTS.move)
        
        # Lưu thống kê
        stats["Total_turns"] += turns
        stats["Total_AI_time"] += ai_time
        
        if winner == 1:
            stats["AI_win"] += 1
            win_str = "My AI (X)"
        elif winner == -1:
            stats["Random_win"] += 1
            win_str = "Random (O)"
        else:
            stats["Draw"] += 1
            win_str = "HÒA"
            
        print(f"#{i:<5} | {win_str:<15} | {turns:<6} | {ai_time:<15.3f} giây | {reason}")

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