import tkinter as tk
import random

# ---------------- НАСТРОЙКИ ----------------
SIZE = 80
ROWS = 8
COLS = 8

PIECES = {
    "P": "♙", "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔",
    "p": "♟", "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚"
}

PIECE_VALUES = {
    "p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 100
}


# ============================================================
#                       КЛАСС ДОСКИ
# ============================================================
class Board:
    def __init__(self):
        self.grid = [
            ["r","n","b","q","k","b","n","r"],
            ["p","p","p","p","p","p","p","p"],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["P","P","P","P","P","P","P","P"],
            ["R","N","B","Q","K","B","N","R"]
        ]

    def inside(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def is_white(self, p):
        return p.isupper()

    def is_black(self, p):
        return p.islower()

    def move_piece(self, sr, sc, er, ec):
        self.grid[er][ec] = self.grid[sr][sc]
        self.grid[sr][sc] = ""

    # ---------------- ПРОВЕРКА ХОДОВ ----------------
    def valid_move(self, sr, sc, er, ec):
        piece = self.grid[sr][sc]
        if piece == "":
            return False

        target = self.grid[er][ec]

        # нельзя бить своих
        if piece.isupper() and target.isupper():
            return False
        if piece.islower() and target.islower():
            return False

        dr = er - sr
        dc = ec - sc
        p = piece.lower()

        # Пешка
        if p == "p":
            direction = -1 if piece.isupper() else 1

            # обычный ход
            if dc == 0 and target == "" and dr == direction:
                return True

            # взятие
            if abs(dc) == 1 and dr == direction and target != "":
                return True

            return False

        # Ладья
        if p == "r":
            return dr == 0 or dc == 0

        # Конь
        if p == "n":
            return (abs(dr), abs(dc)) in [(2, 1), (1, 2)]

        # Слон
        if p == "b":
            return abs(dr) == abs(dc)

        # Ферзь
        if p == "q":
            return dr == 0 or dc == 0 or abs(dr) == abs(dc)

        # Король
        if p == "k":
            return abs(dr) <= 1 and abs(dc) <= 1

        return False


# ============================================================
#                       КЛАСС ИИ
# ============================================================
class AI:
    def __init__(self, board):
        self.board = board

    def all_moves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board.grid[r][c]
                if piece != "" and piece.islower():
                    for nr in range(8):
                        for nc in range(8):
                            if self.board.valid_move(r, c, nr, nc):
                                moves.append((r, c, nr, nc))
        return moves

    # ---------------- ЛЕГКИЙ ----------------
    def easy(self):
        moves = self.all_moves()
        return random.choice(moves) if moves else None

    # ---------------- СРЕДНИЙ ----------------
    def medium(self):
        moves = self.all_moves()
        best = None
        best_score = -1

        for sr, sc, er, ec in moves:
            target = self.board.grid[er][ec]
            score = PIECE_VALUES.get(target.lower(), 0) if target else 0

            if score > best_score:
                best_score = score
                best = (sr, sc, er, ec)

        return best if best else self.easy()

    # ---------------- СЛОЖНЫЙ ----------------
    def hard(self):
        moves = self.all_moves()
        best = None
        best_score = -999

        for sr, sc, er, ec in moves:
            piece = self.board.grid[sr][sc]
            target = self.board.grid[er][ec]

            score = 0

            # взятие
            if target:
                score += PIECE_VALUES.get(target.lower(), 0) * 10

            # центр
            if 2 <= er <= 5 and 2 <= ec <= 5:
                score += 3

            # агрессивные фигуры
            if piece.lower() in ("q", "r"):
                score += 2

            # случайность
            score += random.randint(0, 2)

            if score > best_score:
                best_score = score
                best = (sr, sc, er, ec)

        return best


# ============================================================
#                       КЛАСС ИГРЫ
# ============================================================
class Game:
    def __init__(self, root):
        self.root = root
        self.board = Board()
        self.ai = AI(self.board)

        self.turn = "white"
        self.selected = None

        self.level = tk.StringVar(value="medium")

        self.canvas = tk.Canvas(root, width=SIZE*COLS, height=SIZE*ROWS)
        self.canvas.pack()

        self.status = tk.Label(root, text="Ход белых", font=("Arial", 14))
        self.status.pack(fill="x")

        self.build_ui()

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw()

    # ---------------- UI ----------------
    def build_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="x")

        tk.Label(frame, text="Сложность ИИ:", font=("Arial", 12)).pack(side="left", padx=5)
        for txt, val in [("Легко", "easy"), ("Средне", "medium"), ("Сложно", "hard")]:
            tk.Radiobutton(frame, text=txt, variable=self.level, value=val).pack(side="left")

    # ---------------- РИСОВАНИЕ ----------------
    def draw(self):
        self.canvas.delete("all")

        for r in range(8):
            for c in range(8):
                color = "#F0D9B5" if (r + c) % 2 == 0 else "#B58863"
                x1, y1 = c * SIZE, r * SIZE
                x2, y2 = x1 + SIZE, y1 + SIZE

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                if self.selected == (r, c):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="lime", width=4)

                piece = self.board.grid[r][c]
                if piece:
                    self.canvas.create_text(
                        x1 + SIZE//2, y1 + SIZE//2,
                        text=PIECES[piece],
                        font=("Arial", 42),
                        fill="white" if piece.isupper() else "black"
                    )

    # ---------------- КЛИК ----------------
    def on_click(self, event):
        if self.turn != "white":
            return

        c = event.x // SIZE
        r = event.y // SIZE

        if self.selected:
            sr, sc = self.selected
            piece = self.board.grid[sr][sc]

            if piece.isupper() and self.board.valid_move(sr, sc, r, c):
                self.board.move_piece(sr, sc, r, c)
                self.selected = None
                self.turn = "black"
                self.status.config(text="Ход ИИ")
                self.draw()
                self.root.after(400, self.ai_move)
                return

            self.selected = None

        else:
            if self.board.grid[r][c].isupper():
                self.selected = (r, c)

        self.draw()

    # ---------------- ХОД ИИ ----------------
    def ai_move(self):
        level = self.level.get()

        if level == "easy":
            move = self.ai.easy()
        elif level == "medium":
            move = self.ai.medium()
        else:
            move = self.ai.hard()

        if move:
            sr, sc, er, ec = move
            self.board.move_piece(sr, sc, er, ec)

        self.turn = "white"
        self.status.config(text="Ход белых")
        self.draw()


# ============================================================
#                       ЗАПУСК
# ============================================================
root = tk.Tk()
root.title("Шахматы с ИИ")
root.resizable(False, False)

Game(root)

root.mainloop()
