﻿################################################################################

# User Interface

# wrapped_parser
# The new parser can be used as a drop in replacement of the old parser,
#   supporting both wrapped ( i.e. loads ) and unchanged ( i.e. dumps )
#   methods
from .package import JsonComment

# Allows any JSON parser to ignore comments, accept multiline strings and
#   a trailing comma in objects/arrays
# (json_parser_module)
# Module or Class Instance, which supports JSON load/loads interface

################################################################################

# Developer Interface

# wrapped_item
# An instance mimicking the wrapped object
from .package import GenericWrapper

# Simulates dynamic inheritance of Classes and Modules.
#   Wrapper and Wrapped states are kept independent, unlike common
#   inheritance.
# This class should only be inherited from.
#   Inheriting classes can access their wrapped object via
#   self.object_to_wrap
# (object_to_wrap)
# Module or Class Instance to be wrapped

# Use example:
# class WrapMyClass(GenericWrapper):
# # Preprocess part of the call to method1,
# #   then call method1 of the wrapped object
# def method1 (self, some_variable, *args, **kwargs):
# new_variable = do something with some_variable
# return self.object_to_wrap.method1(
#   new_variable, *args, **kwargs
# )
# # Substitute method2 of the wrapped object
# def method2 (self, some_variable1, some_variable2):
# result = do something
# return result

# # Wraps a class instance
# wrapped_class = WrapMyClass(MyClass())
# # The wrapped method
# print(wrapped_class.method1(some_variable, something_else))
# # The changed method
# print(wrapped_class.method2(some_variable1, some_variable2))
# # The original method, untouched by the wrapper
# print(wrapped_class.method3(anything))

################################################################################
