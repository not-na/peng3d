
################################################################################

from types import ModuleType

################################################################################

# A Class to simulate dynamic inheritance
# Allows to change behaviour of multiple modules or classes, with the same
	# interface
# Note: Class wrapping only partially tested
class GenericWrapper:

	# object_to_wrap can be:
	# A Module
	# A Class Instance
	def __init__(self, object_to_wrap):
		self.object_to_wrap = object_to_wrap
		if isinstance(object_to_wrap, ModuleType):
			self._lookup = lambda name : self.object_to_wrap.__dict__[name]
		elif isinstance(object_to_wrap, object):
			self._lookup = self.object_to_wrap.__getattr__
		else:
			raise TypeError("Expected a Module or a Class Instance")

	# Fallback lookup for undefined methods
	def __getattr__(self, name):
		return self._lookup(name)

################################################################################
