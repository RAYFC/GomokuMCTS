import tkinter as tk
import math
import pickle
from game_board import Board
from mcts import MCTSPlayer
from player import HumanPlayer
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, \
                       PASS, is_black_white, coord_to_point, where1d, \
                       MAXSIZE, NULLPOINT, LEFTBUTTON

class BoardCanvas(tk.Canvas):
	"""Apply the tkinter Canvas Widget to plot the game board and stones."""
	
	def __init__(self, master=None, height=0, width=0):
		
		tk.Canvas.__init__(self, master, height=height, width=width)
		self.draw_gameBoard()
		self.turn = BLACK
		self.undo = False
		self.depth = 2
		self.prev_exist = False
		self.prev_row = 0
		self.prev_col = 0

		self.initPlayers()
		

	def initPlayers(self):
		self.width = 9
		self.height = 9
		self.board = Board(width=self.width, height=self.height, n_in_row=5)
		self.mcts_player = MCTSPlayer(c_puct=5, n_playout=1000)
		self.human_player = HumanPlayer()

		self.start_player = 0	# 0 - human, 1 - mcts_player

		self.board.init_board(self.start_player)
		p1, p2 = self.board.players
		self.human_player.set_player_id(p1)
		self.mcts_player.set_player_id(p2)
		self.players = {p2: self.mcts_player, p1: self.human_player}
		self.board.show(self.human_player.playerId, self.mcts_player.playerId)


	def draw_gameBoard(self):
		"""Plot the game board."""

		# 9 horizontal lines
		for i in range(9):
			start_pixel_x = (i + 1) * 30
			start_pixel_y = (0 + 1) * 30
			end_pixel_x = (i + 1) * 30
			end_pixel_y = (8 + 1) * 30
			self.create_line(start_pixel_x, start_pixel_y, end_pixel_x, end_pixel_y)

		# 9 vertical lines
		for j in range(9):
			start_pixel_x = (0 + 1) * 30
			start_pixel_y = (j + 1) * 30
			end_pixel_x = (8 + 1) * 30
			end_pixel_y = (j + 1) * 30
			self.create_line(start_pixel_x, start_pixel_y, end_pixel_x, end_pixel_y)

		# place a "star" to particular intersections 
		self.draw_star(2, 2)
		self.draw_star(6, 2)
		self.draw_star(4, 4)
		self.draw_star(2, 6)
		self.draw_star(6, 6)


	def draw_star(self, row, col):
		"""Draw a "star" on a given intersection
		
		Args:
			row, col (i.e. coord of an intersection)
		"""
		start_pixel_x = (row + 1) * 30 - 2
		start_pixel_y = (col + 1) * 30 - 2
		end_pixel_x = (row + 1) * 30 + 2
		end_pixel_y = (col + 1) * 30 + 2
		
		self.create_oval(start_pixel_x, start_pixel_y, end_pixel_x, end_pixel_y, fill=GoBoardUtil.color_string(BLACK))


	def draw_stone(self, row, col):
		"""Draw a stone (with a circle on it to denote latest move) on a given intersection.
		
		Specify the color of the stone depending on the turn.
		
		Args:
			row, col (i.e. coord of an intersection)
		"""

		inner_start_x = (row + 1) * 30 - 4
		inner_start_y = (col + 1) * 30 - 4
		inner_end_x = (row + 1) * 30 + 4
		inner_end_y = (col + 1) * 30 + 4

		outer_start_x = (row + 1) * 30 - 6
		outer_start_y = (col + 1) * 30 - 6
		outer_end_x = (row + 1) * 30 + 6
		outer_end_y = (col + 1) * 30 + 6

		start_pixel_x = (row + 1) * 30 - 10
		start_pixel_y = (col + 1) * 30 - 10
		end_pixel_x = (row + 1) * 30 + 10
		end_pixel_y = (col + 1) * 30 + 10

		self.create_oval(start_pixel_x, start_pixel_y, end_pixel_x, end_pixel_y, fill=GoBoardUtil.color_string(self.turn))
		self.create_oval(outer_start_x, outer_start_y, outer_end_x, outer_end_y, fill=GoBoardUtil.color_string(GoBoardUtil.opponent(self.turn)))
		self.create_oval(inner_start_x, inner_start_y, inner_end_x, inner_end_y, fill=GoBoardUtil.color_string(self.turn))


	def draw_prev_stone(self, row, col):
		"""Draw the previous stone with single color.
		
		Specify the color of the stone depending on the turn.
		
		Args:
			row, col (i.e. coord of an intersection)
		"""
		
		start_pixel_x = (row + 1) * 30 - 10
		start_pixel_y = (col + 1) * 30 - 10
		end_pixel_x = (row + 1) * 30 + 10
		end_pixel_y = (col + 1) * 30 + 10

		self.create_oval(start_pixel_x, start_pixel_y, end_pixel_x, end_pixel_y, fill=GoBoardUtil.color_string(GoBoardUtil.opponent(self.turn)))


	def isValidClickPos(self, event, row, col):
		"""Since there is only one intersection such that the distance between it 
		and where the user clicks is less than 9, it is not necessary to find 
		the actual least distance
		"""
		pixel_x = (row + 1) * 30
		pixel_y = (col + 1) * 30
		square_x = math.pow((event.x - pixel_x), 2)
		square_y = math.pow((event.y - pixel_y), 2)
		return math.sqrt(square_x + square_y) < 9


	def check_win(self):
		"""If the user wins the game, end the game and unbind."""
		end, winner = self.board.game_end()
		if end:
			if winner != -1:
				message = GoBoardUtil.color_string(self.turn).upper() + " WINS"
				print("{} WINS".format(self.players[winner]))
				self.create_text(150, 320, text=message)
			else:
				print("DRAW")
				self.create_text(150, 320, text='DRAW')
			self.unbind(LEFTBUTTON)
		return end, winner


	def gameLoop(self, event):
		"""The main loop of the game. 
		Note: The game is played on a tkinter window. However, there is some quite useful information 
			printed onto the terminal such as the simple visualizaiton of the board after each turn,
			messages indicating which step the user reaches at, and the game over message. The user
			does not need to look at what shows up on the terminal. 
		
		self.gameBoard.board()[row][col] == 1(black stone) / 2(white stone)
		self.gameBoard.check() == 1(black wins) / 2(white wins)
		
		Args:
			event (the position the user clicks on using a mouse)
		"""

		while True:
			# User's turn. Place a black stone. 
			print('Your turn now...\n')
			self.turn = 1
			invalid_pos = True
			# since a user might not click exactly on an intersection, place the stone onto
			# the intersection closest to where the user clicks
			for row in range(self.height):
				for col in range(self.width):
					if self.isValidClickPos(event, row, col):
						invalid_pos = False
						self.draw_stone(row, col)
						if self.prev_exist == False:
							self.prev_exist = True
						else:
							self.draw_prev_stone(self.prev_row, self.prev_col)
						self.prev_row, self.prev_col = row, col
						# unbind to ensure the user cannot click anywhere until the program
						# has placed a white stone already
						self.unbind(LEFTBUTTON)
						break	# break the inner for loop
				else:
					continue	# executed if the inner for loop ended normally(no break)
				break			# executed if 'continue' skipped(break)
								# break the outer for loop
			
			# break the inner while loop
			if invalid_pos:
				print('Invalid position.\n')
				break
			else:
				break

		# Place a black stone after determining the position
		move = self.board.location_to_move([row, col])
		self.board.do_move(move)
		self.board.show(self.human_player.playerId, self.mcts_player.playerId)
		print('\n')

		end, winner = self.check_win()
		if end:
			return winner
		
		# Change the turn to the program now
		self.turn = 2
		print('Program is thinking now...')
		
		# Determine the position the program will place a white stone on.
		# Place a white stone after determining the position.
		move = self.mcts_player.get_action(self.board)
		self.board.do_move(move)

		row, col = self.board.move_to_location(move)
		coord = '%s%s'%(chr(ord('A') + row), col + 1)
		print('Program has moved to {}\n'.format(coord))
		self.draw_stone(row,col)
		if self.prev_exist == False:
			self.prev_exist = True
		else:
			self.draw_prev_stone(self.prev_row, self.prev_col)
		self.prev_row, self.prev_col = row, col
		self.board.show(self.human_player.playerId, self.mcts_player.playerId)
		print('\n')

		# bind after the program makes its move so that the user can continue to play
		self.bind(LEFTBUTTON, self.gameLoop)

		end, winner = self.check_win()
		if end:
			return winner
			

class BoardFrame(tk.Frame):
	"""The Frame Widget is mainly used as a geometry master for other widgets, or to
	provide padding between other widgets.
	"""
	
	def __init__(self, master = None):
		tk.Frame.__init__(self, master)
		self.create_widgets()


	def create_widgets(self):
		self.boardCanvas = BoardCanvas(height = 370, width = 300)
		self.boardCanvas.bind(LEFTBUTTON, self.boardCanvas.gameLoop)
		self.boardCanvas.pack()
