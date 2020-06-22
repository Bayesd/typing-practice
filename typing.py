#!/bin/python3

import sys
import time
import argparse

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
#
# max_fails - How many failed attempts before a failure. Pass negative to not fail.
#
# returns (
# 	bool  success     - Did the user successfully complete the line?
# 	float time_taken  - How long did they take on the successful attempt. None if they failed.
# 	int   total_chars - How many characters did the user type in total, including failed attempts?
# 	int   total_time  - How long did the user spend on all attempts? Excludes time spent between attempts.
# )
def practice_line(string, max_fails=10):
	# Print the string for the user to copy.
	sys.stdout.write(fg(CYAN) + bold + string + reset + "\n")

	str_progress = 0
	start_time = None
	failures_remaining = int(max_fails)

	total_chars = 0
	total_time = 0

	while str_progress < len(string):
		# Read a character of user input
		user_char = get_char()
		correct_char = string[str_progress]

		# If they typed the correct character, echo it
		# out, and progress to the next character.
		if user_char == correct_char:
			sys.stdout.write(correct_char)
			sys.stdout.flush()

			total_chars += 1

			if str_progress == 0:
				start_time = time.time()

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

			total_time += time.time() - start_time
			total_chars += 1

			start_time = None

			failures_remaining -= 1
			if failures_remaining == 0:
				return False, None, total_chars, total_time

			str_progress = 0

	sys.stdout.write("\n")

	time_elapsed = None
	if start_time is not None:
		end_time = time.time()
		time_elapsed = end_time - start_time
		total_time += time_elapsed

	return True, time_elapsed, total_chars, total_time

# Practice a passage consisting of several lines
def practice_passage(lines, fail_lines=10):
	# Time/chars on successful attempts
	total_correct_time = 0
	total_correct_chars = 0

	# Time/chars on all attempts
	total_time = 0
	total_chars = 0
	
	current_progress = 0
	while current_progress < len(lines):
		line = lines[current_progress]

		success, time_taken, total_line_chars, total_line_time = practice_line(line, max_fails=fail_lines)

		total_time += total_line_time
		total_chars += total_line_chars

		if success:
			total_correct_time += time_taken
			total_correct_chars += len(line)
			current_progress += 1
		elif current_progress > 0:
			current_progress -= 1
	
	wpm_correct = total_correct_chars / total_correct_time * 12
	wpm_all     = total_chars         / total_time         * 12
	
	sys.stdout.write(fg(GREEN) + f"Speed (all):     {wpm_all    :.1f} wpm" + reset + "\n")
	sys.stdout.write(fg(GREEN) + f"Speed (correct): {wpm_correct:.1f} wpm" + reset + "\n")

if __name__ == "__main__":
	parser = argparse.ArgumentParser("Typing Practice")

	parser.add_argument("--fail-lines", "-f", type=int, default=10,
		help="How many failures before the user fails the line?")

	args = parser.parse_args()

	if not sys.stdin.isatty():
		sys.stderr.write("This program must be run in a terminal")
		sys.exit(1)
	
	import wikisample
	
	sample_lines = []
	while len(sample_lines) < 5:
		sample_lines = wikisample.get_article(lang="simple")

	sample_lines = sample_lines[0:10]
	practice_passage(sample_lines, fail_lines=args.fail_lines)
