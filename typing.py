#!/bin/python3

import sys

# Placeholder string. This should be replaced with a
# proper way of retrieving/generating practice text.
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

# Control Sequence Introducer
CSI = "\x1b["

# Colour values which may be set to foreground or background in a tty
BLACK        = 0
RED          = 1
GREEN        = 2
BLUE         = 4
YELLOW       = RED  | GREEN
MAGENTA      = RED  | BLUE
CYAN         = BLUE | GREEN
WHITE        = RED  | GREEN | BLUE
RESET_COLOUR = 9

def fg(colour):
	return CSI + "3" + str(colour) + "m"

reset        = CSI +  "0m"
bold         = CSI +  "1m"
inverse      = CSI +  "7m"
reset_weight = CSI + "22m"

# Require the user to correctly enter the given string.
def practice_line(string):
	# Print the string for the user to copy.
	sys.stdout.write(fg(CYAN) + bold + string + reset + "\n")

	str_progress = 0
	while str_progress < len(string):
		# Read a character of user input
		user_char = get_char()
		correct_char = string[str_progress]

		# If they typed the correct character, echo it
		# out, and progress to the next character.
		if user_char == correct_char:
			sys.stdout.write(correct_char)
			sys.stdout.flush()

			str_progress += 1

		# Exit on Ctrl-C
		elif user_char == "\x03":
			sys.exit(0)

		# If they typed the wrong character (except on the very first character),
		# Print the wrong character out, reset the string.
		elif str_progress > 0:
			display_char = user_char
			if display_char == "\n":
				display_char = ""

			sys.stdout.write(fg(RED) + bold + display_char + reset + "\n")
			sys.stdout.flush()

			str_progress = 0
	
	sys.stdout.write("\n")

if __name__ == "__main__":
	if not sys.stdin.isatty():
		sys.stderr.write("This program must be run in a terminal")
		sys.exit(1)
	
	import wikisample
	
	sample_lines = []
	while len(sample_lines) < 5:
		sample_lines = wikisample.get_article(lang="simple")
	
	for line in sample_lines:
		practice_line(line)
