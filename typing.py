#!/bin/python3

import sys
import math
import time
import argparse

# How long to consider a break between keys. In seconds.
# Intervals longer than this won't be considered during speed calculations.
MAX_KEY_INTERVAL = 10

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

bell = "\a"

# Holds stats about one or more attempts at typing a line.
class SessionStats:
	__slots__ = [
		# Stats for correct line attempts
		"correct_seconds",
		"correct_chars",

		# Stats for all attempts
		"total_seconds",
		"total_chars",

		# Stats for the current line attempt
		"attempt_seconds",
		"attempt_chars",

		# Timestamp for the last character typed, or None at the start of a line
		"last_key_time",
	]

	def __init__(self):
		self.correct_seconds = 0
		self.correct_chars = 0

		self.total_seconds = 0
		self.total_chars = 0

		self.attempt_seconds = 0
		self.attempt_chars = 0

		self.last_key_time = None

	def type_char(self):
		now = time.time()

		if self.last_key_time is not None:
			elapsed = now - self.last_key_time
		else:
			elapsed = math.inf

		self.last_key_time = now

		# If the user had a long break between this key and the last, don't count the keystroke for timing/wpm purposes
		if elapsed > MAX_KEY_INTERVAL:
			return

		self.total_seconds += elapsed
		self.attempt_seconds += elapsed

		self.total_chars += 1
		self.attempt_chars += 1

	def end_attempt(self, success=False):
		if success:
			self.correct_seconds += self.attempt_seconds
			self.correct_chars += self.attempt_chars

		self.attempt_seconds = 0
		self.attempt_chars = 0

		self.last_key_time = None
	
	def total_wpm(self):
		return self.total_chars / self.total_seconds * 12
	
	def correct_wpm(self):
		return self.correct_chars / self.correct_seconds * 12
	
	def __iadd__(self, other):
		self.correct_seconds += other.correct_seconds
		self.correct_chars += other.correct_chars

		self.total_seconds += other.total_seconds
		self.total_chars += other.total_chars

		return self

# Require the user to correctly enter the given string.
#
# max_fails - How many failed attempts before a failure. Pass negative to not fail.
#
# returns (
# 	bool         success - Did the user successfully complete the line?
# 	SessionStats stats   - Statistics such as characters typed and taken.
# )
def practice_line(string, max_fails=10):
	# Print the string for the user to copy.
	sys.stdout.write(fg(CYAN) + bold + string + reset + "\n")

	str_progress = 0
	failures_remaining = int(max_fails)

	stats = SessionStats()

	while str_progress < len(string):
		# Read a character of user input
		user_char = get_char()
		correct_char = string[str_progress]

		# If they typed the correct character, echo it
		# out, and progress to the next character.
		if user_char == correct_char:
			sys.stdout.write(correct_char)
			sys.stdout.flush()

			stats.type_char()

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

			sys.stdout.write(bell + fg(RED) + bold + display_char + reset + "\n")

			stats.type_char()
			stats.end_attempt(False)

			failures_remaining -= 1
			if failures_remaining == 0:
				return False, stats

			str_progress = 0

		# If the user mis-types the first letter of the line, don't penalise them for it.
		else:
			sys.stdout.write(bell)
			sys.stdout.flush()

	sys.stdout.write("\n")

	stats.end_attempt(True)
	return True, stats

# Practice a passage consisting of several lines
def practice_passage(lines, fail_lines=10):
	stats = SessionStats()
	current_progress = 0
	while current_progress < len(lines):
		line = lines[current_progress]

		success, line_stats = practice_line(line, max_fails=fail_lines)

		stats += line_stats

		if success:
			current_progress += 1
		elif current_progress > 0:
			current_progress -= 1
	
	sys.stdout.write(fg(GREEN) + f"Speed (all):     {stats.total_wpm()  :.1f} wpm" + reset + "\n")
	sys.stdout.write(fg(GREEN) + f"Speed (correct): {stats.correct_wpm():.1f} wpm" + reset + "\n")

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
