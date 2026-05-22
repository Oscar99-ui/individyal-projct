import tkinter as tk
from tkinter import messagebox

BOARD_SIZE = 8
CELL_SIZE = 80

PIECES = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
}


class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title('Шахматы на Python')

        self.canvas = tk.Canvas(
            root,
            width=BOARD_SIZE * CELL_SIZE,
            height=BOARD_SIZE * CELL_SIZE
        )
        self.canvas.pack()

        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]

        self.selected = None
        self.turn = 'white'

        self.canvas.bind('<Button-1>', self.click)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete('all')

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                color = '#F0D9B5' if (row + col) % 2 == 0 else '#B58863'

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline='black'
                )

                piece = self.board[row][col]

                if piece:
                    self.canvas.create_text(
                        x1 + CELL_SIZE // 2,
                        y1 + CELL_SIZE // 2,
                        text=PIECES[piece],
                        font=('Arial', 36)
                    )

        if self.selected:
            row, col = self.selected

            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            self.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                outline='red',
                width=4
            )

    def click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if row < 0 or row >= 8 or col < 0 or col >= 8:
            return

        if self.selected is None:

            piece = self.board[row][col]

            if piece:

                if self.turn == 'white' and piece.isupper():
                    self.selected = (row, col)

                elif self.turn == 'black' and piece.islower():
                    self.selected = (row, col)

        else:

            old_row, old_col = self.selected

            self.move_piece(old_row, old_col, row, col)

            self.selected = None

        self.draw_board()

    def is_path_clear(self, old_row, old_col, new_row, new_col):

        row_step = 0 if new_row == old_row else (
            1 if new_row > old_row else -1
        )

        col_step = 0 if new_col == old_col else (
            1 if new_col > old_col else -1
        )

        row = old_row + row_step
        col = old_col + col_step

        while (row, col) != (new_row, new_col):

            if self.board[row][col] != '':
                return False

            row += row_step
            col += col_step

        return True

    def move_piece(self, old_row, old_col, new_row, new_col):

        piece = self.board[old_row][old_col]

        if old_row == new_row and old_col == new_col:
            return

        target = self.board[new_row][new_col]

        if target:

            if piece.isupper() and target.isupper():
                return

            if piece.islower() and target.islower():
                return

        piece_type = piece.lower()

        # Пешки
        if piece_type == 'p':

            row_delta = new_row - old_row
            col_delta = abs(new_col - old_col)

            # Белые пешки
            if piece.isupper():

                if row_delta > 0 or row_delta == 0:
                    return

                # Первый ход на 2 клетки
                if (
                    row_delta == -2
                    and old_row == 6
                    and old_col == new_col
                    and self.board[5][old_col] == ''
                    and self.board[4][old_col] == ''
                ):
                    pass

                # Обычный ход
                elif (
                    row_delta == -1
                    and old_col == new_col
                    and target == ''
                ):
                    pass

                # Взятие
                elif (
                    row_delta == -1
                    and col_delta == 1
                    and target != ''
                ):
                    pass

                else:
                    return

            # Чёрные пешки
            else:

                if row_delta < 0 or row_delta == 0:
                    return

                # Первый ход на 2 клетки
                if (
                    row_delta == 2
                    and old_row == 1
                    and old_col == new_col
                    and self.board[2][old_col] == ''
                    and self.board[3][old_col] == ''
                ):
                    pass

                # Обычный ход
                elif (
                    row_delta == 1
                    and old_col == new_col
                    and target == ''
                ):
                    pass

                # Взятие
                elif (
                    row_delta == 1
                    and col_delta == 1
                    and target != ''
                ):
                    pass

                else:
                    return

        # Ладья
        elif piece_type == 'r':

            if old_row != new_row and old_col != new_col:
                return

            if not self.is_path_clear(
                old_row,
                old_col,
                new_row,
                new_col
            ):
                return

        # Слон
        elif piece_type == 'b':

            if abs(new_row - old_row) != abs(new_col - old_col):
                return

            if not self.is_path_clear(
                old_row,
                old_col,
                new_row,
                new_col
            ):
                return

        # Ферзь
        elif piece_type == 'q':

            straight = (
                old_row == new_row
                or old_col == new_col
            )

            diagonal = (
                abs(new_row - old_row)
                == abs(new_col - old_col)
            )

            if not straight and not diagonal:
                return

            if not self.is_path_clear(
                old_row,
                old_col,
                new_row,
                new_col
            ):
                return

        # Конь
        elif piece_type == 'n':

            if (
                abs(new_row - old_row),
                abs(new_col - old_col)
            ) not in [(2, 1), (1, 2)]:
                return

        # Король
        elif piece_type == 'k':

            if (
                abs(new_row - old_row) > 1
                or abs(new_col - old_col) > 1
            ):
                return

        # Делаем ход
        self.board[new_row][new_col] = piece
        self.board[old_row][old_col] = ''

        # Победа
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

        # Смена хода
        self.turn = (
            'black'
            if self.turn == 'white'
            else 'white'
        )

if __name__ == '__main__':
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()

