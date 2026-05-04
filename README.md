# Bài tập lớn 2 - Môn Nhập môn Trí tuệ Nhân tạo: Game Playing

Bài tập lớn này xây dựng một hệ thống Trí tuệ Nhân tạo (AI Agent) có khả năng chơi tự động bộ môn Cờ Gánh. Hệ thống áp dụng thuật toán Minimax kết hợp Alpha-Beta Pruning, Iterative Deepening và Lazy BFS Heuristics để tự động tính toán nước đi tối ưu qua hàm `def move(board, player, remain_time)`. AI được tối ưu hóa để đưa ra quyết định nhanh chóng trong quỹ thời gian 99 giây cho toàn bộ ván đấu và không vượt quá 3 giây cho mỗi nước đi .

## 📂 Cấu trúc thư mục (Project Structure)

```text
BTL2-GAME-PLAYING/
├── a2_260408.py           # Core engine xử lý luật chơi Cờ Gánh và tác nhân Random (NPC)
├── my_agent.py            # Mã nguồn chính của tác nhân AI (chứa thuật toán cốt lõi)
├── gui_referee.py         # Môi trường mô phỏng trực quan (Pygame) để theo dõi trận đấu
├── referee.py             # Script chạy giải đấu tự động và thống kê hiệu năng (Benchmark)
└── README.md              # Tài liệu hướng dẫn cài đặt và sử dụng
```

## 🚀 Hướng dẫn Cài đặt (Installation)

**Bước 1:** Clone repository này về máy hoặc giải nén thư mục bài tập lớn. Mở Terminal tại thư mục gốc của dự án.

**Bước 2:** Cài đặt các thư viện Python cần thiết (để hiển thị giao diện mô phỏng) bằng lệnh:
```bash
pip install pygame
```

## 🎮 Hướng dẫn Sử dụng (Usage)

**1. Chạy Đánh giá Hiệu năng tự động (CLI Benchmark):**
Script này sẽ cho AI của bạn thi đấu trực tiếp với Random Agent 10 trận liên tiếp trong terminal (không mở giao diện). Hệ thống sẽ tự động in ra bảng thống kê Tỷ lệ thắng, số lượt trung bình và thời gian suy nghĩ trung bình của AI.
```bash
python referee.py
```

**2. Chạy Giao diện Trực quan (Pygame Replay Tool):**
Mở môi trường GUI trực quan để theo dõi từng nước đi của AI đấu với Random NPC. Công cụ này bao gồm bảng thống kê thời gian thực (Match Statistics) và các nút điều khiển (Prev, Pause/Play, Next) để bạn dễ dàng debug hoặc trình diễn thuật toán.
```bash
python gui_referee.py
```

**3. Chạy Test độc lập tác nhân AI:**
Để chạy một kịch bản test nhanh trên terminal (AI X đấu với NPC O), sử dụng lệnh:
```bash
python my_agent.py
```