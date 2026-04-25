import tkinter as tk
import sys
import os
import random

# ===== FIX: chặn print khi import =====
original_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
from Co_ganh import *
sys.stdout.close()
sys.stdout = original_stdout
# =====================================

CELL = 80

# ================= AGENTS =================
def agent_X(board, player, mo):

    return npc_move(board, player, mo)

def agent_O(board, player, mo):

    return npc_move(board, player, mo)
# ==========================================


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Cờ Gánh UI")

        self.canvas = tk.Canvas(root, width=5*CELL, height=5*CELL)
        self.canvas.pack()

        # ===== BUTTONS =====
        frame = tk.Frame(root)
        frame.pack()

        tk.Button(frame, text="Auto Move (X)", command=self.auto_move).pack(side="left")
        tk.Button(frame, text="Auto Play", command=self.auto_play).pack(side="left")
        tk.Button(frame, text="Stop", command=self.stop_auto).pack(side="left")
        tk.Button(frame, text="Reset", command=self.reset).pack(side="left")

        self.status = tk.Label(root, text="Player: X")
        self.status.pack()

        # ===================

        self.board = init_board()
        self.player = 1
        self.selected = None
        self.mo = []
        self.running = False

        self.canvas.bind("<Button-1>", self.click)

        self.draw()

    # ================= DRAW =================
    def draw(self):
        self.canvas.delete("all")

        for i in range(5):
            for j in range(5):
                x1 = j * CELL
                y1 = i * CELL
                x2 = x1 + CELL
                y2 = y1 + CELL

                self.canvas.create_rectangle(x1, y1, x2, y2)

                val = self.board[4 - i][j]
                if val == 1:
                    self.canvas.create_text((x1+x2)//2, (y1+y2)//2,
                                            text="X", font=("Arial", 24))
                elif val == -1:
                    self.canvas.create_text((x1+x2)//2, (y1+y2)//2,
                                            text="O", font=("Arial", 24))

        # highlight chọn
        if self.selected:
            r, c = self.selected
            x1 = c * CELL
            y1 = (4 - r) * CELL
            x2 = x1 + CELL
            y2 = y1 + CELL
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         outline="red", width=3)

        self.status.config(text=f"Player: {'X' if self.player==1 else 'O'}")

    # ================= HUMAN MOVE =================
    def click(self, event):
        if self.running:
            return

        if self.player != 1:
            return

        col = event.x // CELL
        row = 4 - (event.y // CELL)

        if self.selected is None:
            if self.board[row][col] == 1:
                self.selected = (row, col)
        else:
            move = (self.selected, (row, col))
            valid_moves = get_valid_moves(self.board, self.player)

            if move in valid_moves:
                self.mo = act_moves(move, self.player, self.board)
                self.player = -1
                self.selected = None
                self.draw()
                self.root.after(300, self.npc_turn)
            else:
                print("Move sai:", move)
                self.selected = None

        self.draw()

    # ================= NPC TURN =================
    def npc_turn(self):
        move = agent_O(self.board, self.player, self.mo)

        if move is None:
            print("🏆 Bạn thắng!")
            self.running = False
            return

        self.mo = act_moves(move, self.player, self.board)
        self.player = 1
        self.draw()

        if not get_valid_moves(self.board, self.player):
            print("💀 Bạn hết nước đi → Thua!")
            self.running = False

    # ================= AUTO MOVE X =================
    def auto_move(self):
        if self.player != 1:
            return

        move = agent_X(self.board, self.player, self.mo)

        if move is None:
            print("💀 X thua!")
            return

        self.mo = act_moves(move, self.player, self.board)
        self.player = -1
        self.draw()
        self.root.after(300, self.npc_turn)

    # ================= AUTO PLAY =================
    def auto_play(self):
        self.running = True
        self.loop_auto()

    def loop_auto(self):
        if not self.running:
            return

        if self.player == 1:
            move = agent_X(self.board, self.player, self.mo)
        else:
            move = agent_O(self.board, self.player, self.mo)

        if move is None:
            winner = "O" if self.player == 1 else "X"
            print(f"🏆 Winner: {winner}")
            self.running = False
            return

        self.mo = act_moves(move, self.player, self.board)
        self.player *= -1
        self.draw()

        self.root.after(300, self.loop_auto)

    def stop_auto(self):
        self.running = False

    def reset(self):
        self.board = init_board()
        self.player = 1
        self.selected = None
        self.mo = []
        self.running = False
        self.draw()


# ================= MAIN =================
if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()