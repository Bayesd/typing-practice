#!/bin/python3

import re

import wikipedia as wiki
import nltk

# List of characters which may be accessed from a standard english keyboard.
english_chars = "pyfgcrlaoeuidhtnsqjkxbmwvzPYFGCRLAOEUIDHTNSQJKXBMWVZ 1234567890!\"$%^&*()[]{}'@,.<>/?=+-_#~;:"

# Certain characters can't exactly be typed, but have close approximations
equivalent_chars = {
	"\u2013": "-",
}

# Get an article from wikipedia. Return as a list of sentences.
# If title is omitted, a random page will be chosen.
def get_article(title=None, lang="en"):
	if lang is not None:
		wiki.set_lang(lang)

	if title is None:
		title = wiki.random()
	
	page = wiki.page(title)

	return [title, *sanitise_article(page.content)]

# Tests if a string contains only allowed characters.
# Returns the validated string or None if invalid.
def is_allowed(string, allowed_chars=english_chars, substitutions=equivalent_chars):
	validated_string = ""

	for char in string:
		if char in substitutions:
			char = substitutions[char]

		if char not in allowed_chars:
			return None

		validated_string += char

	return validated_string

# Cleans up unwanted sections in an article.
def sanitise_article(text):
	# Remove sections "References", "Other websites", "Related pages", "More reading"
	# (these appear when using simple english)
	# They always appear wrapped in two equals signs
	text = re.sub(r"== (?:References|Other websites|Related pages|More reading) ==.*", "",
		text, flags=re.S | re.M)

	# Remove equals signs from section names
	text = re.sub(r"={2,}", "", text)

	# Contract ellipses into just three dots (They sometimes appear as 4+)
	text = re.sub(r"\.{3,}", "...", text)

	# split into sentences
	lines = nltk.tokenize.sent_tokenize(text)

	# Further split into lines
	lines = [ln for sentence in lines for ln in re.split(r"\n", sentence)]

	# Strip excess whitespace
	lines = [ln.strip() for ln in lines]
	lines = [re.sub(r"\s+", " ", ln) for ln in lines]

	# Filter out short sentences
	lines = [ln for ln in lines if len(ln) > 3]

	# Filter out lines containing LaTeX
	lines = [ln for ln in lines if not re.search(r"\\displaystyle", ln)]

	# Filter out lines with un-typable characters
	lines = [is_allowed(ln) for ln in lines]
	lines = [ln for ln in lines if ln is not None]

	# Split long bracketed phrases at the end of sentences.
	lines = [ln for sentence in lines for ln in re.split(r" (\(.{10,}\)\.)", sentence)]
	lines = [ln for ln in lines if ln != ""]

	return lines

if __name__ == "__main__":
	title = None

	content = get_article(title, lang="simple")
	for ln in content:
		print("->\t" + repr(ln))
