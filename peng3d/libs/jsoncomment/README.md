# Json Comment

A wrapper to JSON parsers allowing comments, multiline strings and 
trailing commas

- - -

## Note

This library has been modified by not-na for the peng3d game engine. The modified source code should be contained in this directory.

The file package/comments.py has been modified at line 9 to add JavaScript-style comments, e.g. `//`.

## Dependencies

Python 2.7, 3.3

### Optional

ujson 1.30+

- - -

## Description

JSON Comment allows to parse JSON files or strings with:

* Single and Multi line comments
* Multi line data strings
* Trailing commas in objects and arrays, after the last item

This package works with any JSON parser which supports:

* `load(fp, ...)` to parse files
* `loads(s, ...)` to parse strings

by adding a preprocessor to these calls.

- - -

### Comments

* `#` and `;` are for single line comments
* `/*` and `*/` enclose multiline comments

Inline comments are **not** supported

- - -

### Multiline strings

Any string can be multiline, even object keys.

* Multiline strings start and end with `"""`, like in python
* The preprocessor merges all lines to a single JSON standard string
* A single trailing space per line is kept, if present
* New line is not kept. To hard code new lines in the string, use `\\n`

- - -

## Install

`pip install jsoncomment`

OR

* Download source
* `python setup.py install`

- - -

## Usage

	import json
	from jsoncomment import JsonComment

	string = "[]"
	parser = JsonComment(json)
	parsed_object = parser.loads(string)

### Examples

Added in the /examples directory

- - -

### Limitations

* `#`, `;` and `/*` may be preceded only by whitespaces or tabs on the same line
* `*/` may be followed only by whitespaces or tabs on the same line
* The trailing comma must be the last character on the same line

- - -

## Source

[Source](https://bitbucket.org/Dando_Real_ITA/json-comment/overview)
code available with MIT license on Bitbucket.

- - -

## API

Added in top level `__init__.py`

### How to read the API

API is split in:

	* `User Interface` for common use
	* `Developer Interface` exposing some internals that could be useful

For each item ( function or class ), there are 2 blocks of comments, above 
and below item definition:

	* The top describes the return values
	* The bottom describes the item and call variables

If call variables have defaults or use duck typing, every allowed value is 
described

Example:

	# return_value
		# description
	from .some_module import SomeClass
		# SomeClass description
	# (
		# variable_1,
			# description
		# variable_2 = something,
			# description

			# = Default
				# description of default value ( something )
			# = something_2
				# description of alternate form ( duck typing )
	# )

describes `return_value = SomeClass(variable_1, variable_2 = current_value)`

- - -

## Contact

Dando Real ITA @ [Steam Profile](http://steamcommunity.com/id/dandorealita)
