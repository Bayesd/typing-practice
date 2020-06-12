#!/bin/python3

import sys

practice_string = "Jived fox nymph grabs quick waltz"

# Gets a single character from standard input.
# Does not echo to the screen.
# Adapted from: https://code.activestate.com/recipes/134892/
class GetChar:
	def __init__(self):
		try:
			self.impl = GetCharWin()
		except ImportError:
			self.impl = GetCharUnix()

	def __call__(self):
		return self.impl()

class GetCharUnix:
	def __init__(self):
		import tty
		self.stdin_fd = sys.stdin.fileno()

	def __call__(self):
		import tty, termios

		old_settings = termios.tcgetattr(self.stdin_fd)
		try:
			tty.setraw(self.stdin_fd)
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(self.stdin_fd, termios.TCSADRAIN, old_settings)

		return ch

class GetCharWin:
	def __init__(self):
		import msvcrt

	def __call__(self):
		import msvcrt
		return msvcrt.getch()

get_char = GetChar()

if __name__ == "__main__":
	if not sys.stdin.isatty():
		sys.stderr.write("This program must be run in a terminal")
		sys.exit(1)
	
	sys.stdout.write(practice_string + "\n")

	str_progress = 0
	while str_progress < len(practice_string):
		user_char = get_char()
		correct_char = practice_string[str_progress]

		if user_char == correct_char:
			sys.stdout.write(correct_char)
			str_progress += 1
		elif user_char == "\x03":
			# Exit on Ctrl-C
			sys.exit(0)
		else:
			display_char = user_char
			if display_char == "\n":
				display_char = ""
			sys.stdout.write(display_char + "\n")
			str_progress = 0

		sys.stdout.flush()
	
	sys.stdout.write("\n")
