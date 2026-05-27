import tkinter as tk
from tkinter import messagebox
import random

BOARD_SIZE = 8
CELL_SIZE = 80

PIECES = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
}


class ChessGame:

    # Инициализация игры
    # создание окна, доски и выбор стороны
    def __init__(self, root):

        self.root = root
        self.root.title('Шахматы с ИИ')

        self.canvas = tk.Canvas(
            root,
            width=BOARD_SIZE * CELL_SIZE,
            height=BOARD_SIZE * CELL_SIZE
        )
        self.canvas.pack()

        # выбор стороны игрока
        self.player_color = self.choose_side()

        # цвет ИИ
        self.ai_color = (
            'black'
            if self.player_color == 'white'
            else 'white'
        )

        # начальная расстановка фигур
        self.board = [
            ['r','n','b','q','k','b','n','r'],
            ['p','p','p','p','p','p','p','p'],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['P','P','P','P','P','P','P','P'],
            ['R','N','B','Q','K','B','N','R']
        ]

        self.selected = None
        self.turn = 'white'

        # обработка клика мышкой
        self.canvas.bind('<Button-1>', self.click)

        # рисование доски
        self.draw_board()

        # если ИИ белый — он ходит первым
        if self.ai_color == 'white':
            self.root.after(500, self.ai_move)

    # выбор стороны
    def choose_side(self):

        result = tk.StringVar(value='white')

        window = tk.Toplevel(self.root)
        window.title('Выбор стороны')
        window.geometry('250x150')

        tk.Label(
            window,
            text='Выберите сторону',
            font=('Arial', 14)
        ).pack(pady=10)

        def choose(color):
            result.set(color)
            window.destroy()

        tk.Button(
            window,
            text='Белые',
            width=15,
            command=lambda: choose('white')
        ).pack(pady=5)

        tk.Button(
            window,
            text='Чёрные',
            width=15,
            command=lambda: choose('black')
        ).pack(pady=5)

        self.root.wait_window(window)
        return result.get()

    # рисование доски и фигур
    def draw_board(self):

        self.canvas.delete('all')

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                color = (
                    '#F0D9B5'
                    if (row + col) % 2 == 0
                    else '#B58863'
                )

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color
                )

                # переворот доски для чёрных
                board_row = row
                board_col = col

                if self.player_color == 'black':
                    board_row = 7 - row
                    board_col = 7 - col

                piece = self.board[board_row][board_col]

                if piece:
                    self.canvas.create_text(
                        x1 + 40,
                        y1 + 40,
                        text=PIECES[piece],
                        font=('Arial', 36)
                    )

        # подсветка выбранной фигуры
        if self.selected:

            row, col = self.selected

            if self.player_color == 'black':
                row = 7 - row
                col = 7 - col

            self.canvas.create_rectangle(
                col * CELL_SIZE,
                row * CELL_SIZE,
                col * CELL_SIZE + CELL_SIZE,
                row * CELL_SIZE + CELL_SIZE,
                outline='red',
                width=3
            )

    # обработка клика игрока
    def click(self, event):

        # нельзя ходить во время ИИ
        if self.turn != self.player_color:
            return

        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        # переворот координат
        if self.player_color == 'black':
            row = 7 - row
            col = 7 - col

        if self.selected is None:

            piece = self.board[row][col]

            if piece:

                if (
                    self.player_color == 'white'
                    and piece.isupper()
                ):
                    self.selected = (row, col)

                elif (
                    self.player_color == 'black'
                    and piece.islower()
                ):
                    self.selected = (row, col)

        else:

            old_row, old_col = self.selected

            moved = self.move_piece(
                old_row,
                old_col,
                row,
                col
            )

            self.selected = None
            self.draw_board()

            # ход ИИ после игрока
            if moved:
                self.root.after(500, self.ai_move)

            return

        self.draw_board()

    # проверка свободного пути
    def is_path_clear(self, old_row, old_col, new_row, new_col):

        row_step = (
            0
            if new_row == old_row
            else (1 if new_row > old_row else -1)
        )

        col_step = (
            0
            if new_col == old_col
            else (1 if new_col > old_col else -1)
        )

        row = old_row + row_step
        col = old_col + col_step

        while (row, col) != (new_row, new_col):

            if self.board[row][col] != '':
                return False

            row += row_step
            col += col_step

        return True

    # проверка допустимого хода
    def is_valid_move(self, old_row, old_col, new_row, new_col):

        piece = self.board[old_row][old_col]
        target = self.board[new_row][new_col]

        if piece == '':
            return False

        # нельзя бить свои фигуры
        if target:
            if piece.isupper() and target.isupper():
                return False
            if piece.islower() and target.islower():
                return False

        piece_type = piece.lower()

        # пешка
        if piece_type == 'p':

            direction = -1 if piece.isupper() else 1
            start_row = 6 if piece.isupper() else 1

            if new_col == old_col:

                if (
                    new_row == old_row + direction
                    and target == ''
                ):
                    return True

                if (
                    new_row == old_row + 2 * direction
                    and old_row == start_row
                    and target == ''
                    and self.board[old_row + direction][old_col] == ''
                ):
                    return True

            elif abs(new_col - old_col) == 1:

                if (
                    new_row == old_row + direction
                    and target != ''
                ):
                    return True

            return False

        # ладья
        elif piece_type == 'r':

            if old_row != new_row and old_col != new_col:
                return False

            return self.is_path_clear(
                old_row,
                old_col,
                new_row,
                new_col
            )

        # слон
        elif piece_type == 'b':

            if abs(new_row - old_row) != abs(new_col - old_col):
                return False

            return self.is_path_clear(
                old_row,
                old_col,
                new_row,
                new_col
            )

        # ферзь
        elif piece_type == 'q':

            straight = old_row == new_row or old_col == new_col
            diagonal = abs(new_row - old_row) == abs(new_col - old_col)

            if not (straight or diagonal):
                return False

            return self.is_path_clear(
                old_row,
                old_col,
                new_row,
                new_col
            )

        # конь
        elif piece_type == 'n':

            return (
                abs(new_row - old_row),
                abs(new_col - old_col)
            ) in [(2, 1), (1, 2)]

        # король
        elif piece_type == 'k':

            return (
                abs(new_row - old_row) <= 1
                and abs(new_col - old_col) <= 1
            )

        return False

    # выполнение хода
    def move_piece(self, old_row, old_col, new_row, new_col):

        if not self.is_valid_move(
            old_row,
            old_col,
            new_row,
            new_col
        ):
            return False

        piece = self.board[old_row][old_col]
        target = self.board[new_row][new_col]

        self.board[new_row][new_col] = piece
        self.board[old_row][old_col] = ''

        # проверка победы
        if target and target.lower() == 'k':

            winner = (
                'Белые'
                if piece.isupper()
                else 'Чёрные'
            )

            messagebox.showinfo(
                'Конец игры',
                f'{winner} победили!'
            )

            self.root.quit()

        # смена хода
        self.turn = (
            'black'
            if self.turn == 'white'
            else 'white'
        )

        return True

    # ход ИИ
    def ai_move(self):

        # ИИ ходит только в свой ход
        if self.turn != self.ai_color:
            return

        moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                piece = self.board[row][col]

                if piece == '':
                    continue

                # ИИ играет своим цветом
                if (
                    self.ai_color == 'white'
                    and not piece.isupper()
                ):
                    continue

                if (
                    self.ai_color == 'black'
                    and not piece.islower()
                ):
                    continue

                for new_row in range(BOARD_SIZE):
                    for new_col in range(BOARD_SIZE):

                        if self.is_valid_move(
                            row,
                            col,
                            new_row,
                            new_col
                        ):
                            moves.append(
                                (row, col, new_row, new_col)
                            )

        if moves:

            move = random.choice(moves)

            self.move_piece(
                move[0],
                move[1],
                move[2],
                move[3]
            )

            self.draw_board()


if __name__ == '__main__':
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()