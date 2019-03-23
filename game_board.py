import numpy as np

class Board(object):
    """board for the game"""

    def __init__(self, **kwargs):
        self.width = int(kwargs.get('width', 8))
        self.height = int(kwargs.get('height', 8))
        # board states stored as a dict,
        # key: move as location on the board,
        # value: player as pieces type
        self.states = {}
        # need how many pieces in a row to win
        self.n_in_row = int(kwargs.get('n_in_row', 5))
        self.players = [1, 2]  # player1 and player2

    def init_board(self, start_player=0):
        if self.width < self.n_in_row or self.height < self.n_in_row:
            raise Exception('board width and height can not be '
                            'less than {}'.format(self.n_in_row))
        self.current_player = self.players[start_player]  # start player
        # keep available moves in a list
        self.availables = list(range(self.width * self.height))
        self.states = {}
        self.last_move = -1

    def move_to_location(self, move):
        row = move // self.width
        col = move % self.width
        return [row, col]

    def location_to_move(self, location):
        if len(location) != 2:
            return -1
        row = location[0]
        col = location[1]
        move = row * self.width + col
        if move not in range(self.width * self.height):
            return -1
        return move

    def current_state(self):
        """return the board state from the perspective of the current player.
        state shape: 4*width*height
        """

        square_state = np.zeros((4, self.width, self.height))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width,
                            move_curr % self.height] = 1.0
            square_state[1][move_oppo // self.width,
                            move_oppo % self.height] = 1.0
            # indicate the last move location
            square_state[2][self.last_move // self.width,
                            self.last_move % self.height] = 1.0
        if len(self.states) % 2 == 0:
            square_state[3][:, :] = 1.0  # indicate the colour to play
        return square_state[:, ::-1, :]

    def do_move(self, move):
        self.states[move] = self.current_player
        self.availables.remove(move)
        self.current_player = (
            self.players[0] if self.current_player == self.players[1]
            else self.players[1]
        )
        self.last_move = move

    def has_a_winner(self):
        width = self.width
        height = self.height
        states = self.states
        n = self.n_in_row

        moved = list(set(range(width * height)) - set(self.availables))
        if len(moved) < self.n_in_row *2-1:
            return False, -1

        for m in moved:
            h = m // width
            w = m % width
            player = states[m]

            if (w in range(width - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n))) == 1):
                return True, player

            if (h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * width, width))) == 1):
                return True, player

            if (w in range(width - n + 1) and h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width + 1), width + 1))) == 1):
                return True, player

            if (w in range(n - 1, width) and h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width - 1), width - 1))) == 1):
                return True, player

        return False, -1

    def game_end(self):
        """Check whether the game is ended or not"""
        win, winner = self.has_a_winner()
        if win:
            return True, winner
        elif not len(self.availables):
            return True, -1
        return False, -1

    def get_current_player(self):
        return self.current_player

    def show(self, player1, player2):
        """Output current board on terminal."""
        print('  A B C D E F G H')
        for col in range(self.width):
            print(col + 1, end=" ")
            for row in range(self.height):
                loc = row * self.width + col
                ch = self.states.get(loc, -1)
                if ch == player1:
                    print('X', end=" ")
                elif ch == player2:
                    print('O', end=" ")
                else:
                    print('.', end=" ")
            print()


class GameBoard(object):
    """Game board."""

    def __init__(self):
        # board is a 9*9 array: each posision is initially set to be 0
        self.__board = [[0 for _ in range(9)] for _ in range(9)]

        # store positions of 5 stones in a line
        self.won = {}


    def reset(self):
        """Clear the board (set all position to 0)."""
        self.__board = [[0 for _ in range(9)] for _ in range(9)]


    def get(self, row, col):
        """Get the value at a coord."""
        
        if row < 0 or row >= 9 or col < 0 or col >= 9:
            return 0
        return self.__board[row][col]


    def check(self):
        """Check if there is a winner.

        Returns:
            0-no winner, 1-black wins, 2-white wins
        """
        board = self.__board
        # check in 4 directions
        # a coordinate stands for a specific direction, imagine the direction of a coordinate
        # relative to the origin on xy-axis
        dirs = ((1, -1), (1, 0), (1, 1), (0, 1))
        for i in range(9):
            for j in range(9):
                # if no stone is on the position, don't need to consider this position
                if board[i][j] == 0:
                    continue
                # value-value at a coord, i-row, j-col
                value = board[i][j]
                # check if there exist 5 in a line
                for d in dirs:
                    x, y = i, j
                    count = 0
                    for _ in range(5):
                        if self.get(x, y) != value:
                            break
                        x += d[0]
                        y += d[1]
                        count += 1
                    # if 5 in a line, store positions of all stones, return value
                    if count == 5:
                        self.won = {}
                        r, c = i, j
                        for _ in range(5):
                            self.won[(r, c)] = 1
                            r += d[0]
                            c += d[1]
                        return value
        return 0


    def board(self):
        """Return the board array."""
        return self.__board


    def show(self):
        """Output current board on terminal."""
        print('  A B C D E F G H I')
        self.check()
        for col in range(9):
            print(col + 1, end=" ")
            for row in range(9):
                ch = self.__board[row][col]
                if ch == 0:
                    print('.', end=" ")
                elif ch == 1:
                    print('X', end=" ")
                elif ch == 2:
                    print('O', end=" ")
            print()
