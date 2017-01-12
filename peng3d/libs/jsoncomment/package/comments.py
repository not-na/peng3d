
################################################################################

from .wrapper import GenericWrapper

################################################################################

# Comments
COMMENT_PREFIX = ("#",";","//")
MULTILINE_START = "/*"
MULTILINE_END = "*/"

# Data strings
LONG_STRING = '"""'

################################################################################

class JsonComment(GenericWrapper):

	def loads(self, custom_json_string, *args, **kwargs):
		lines = custom_json_string.splitlines()
		standard_json = json_preprocess(lines)
		return self.object_to_wrap.loads(standard_json, *args, **kwargs)

	def load(self, custom_json_file, *args, **kwargs):
		return self.loads(custom_json_file.read(), *args, **kwargs)

################################################################################

def json_preprocess(lines):

	standard_json = ""
	is_multiline = False
	keep_trail_space = 0

	for line in lines:

		# 0 if there is no trailing space
		# 1 otherwise
		keep_trail_space = int(line.endswith(" "))

		# Remove all whitespace on both sides
		line = line.strip()

		# Skip blank lines
		if len(line) == 0:
			continue

		# Skip single line comments
		if line.startswith(COMMENT_PREFIX):
			continue

		# Mark the start of a multiline comment
		# Not skipping, to identify single line comments using
		#   multiline comment tokens, like
		#   /***** Comment *****/
		if line.startswith(MULTILINE_START):
			is_multiline = True

		# Skip a line of multiline comments
		if is_multiline:
			# Mark the end of a multiline comment
			if line.endswith(MULTILINE_END):
				is_multiline = False
			continue

		# Replace the multi line data token to the JSON valid one
		if LONG_STRING in line:
			line = line.replace(LONG_STRING, '"')

		standard_json += line + " " * keep_trail_space

	# Removing non-standard trailing commas
	standard_json = standard_json.replace(",]", "]")
	standard_json = standard_json.replace(",}", "}")

	return standard_json

################################################################################
