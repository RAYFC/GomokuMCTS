import sys
import tkinter as tk
import warnings
warnings.filterwarnings("ignore")
from board_gui import BoardFrame

def main():
	window = tk.Tk()
	window.wm_title("GOMOKU GAME")
	gui_board = BoardFrame(window)
	gui_board.pack()
	window.mainloop()


if __name__ == "__main__":
	main()