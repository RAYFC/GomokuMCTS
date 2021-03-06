class Player(object):
    def __init__(self):
        self.playerId = None

    def set_player_id(self, playerId):
        self.playerId = playerId

    def get_action(self, board):
        return 0

    def __str__(self):
        return "Player {}".format(self.playerId)


class HumanPlayer(Player):
    def __init__(self):
        super().__init__()

    def get_action(self, board):
        try:
            location = input("Your move: ")
            if isinstance(location, str):  # for python3
                location = [int(n, 10) for n in location.split(",")]
            move = board.location_to_move(location)
        except:
            move = -1
        if move == -1 or move not in board.availables:
            print("invalid move")
            move = self.get_action(board)
        return move
