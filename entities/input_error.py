from dataclasses import dataclass



@dataclass(order=True)
class InputError:
	"""
	Containes error message for input errors
	"""
	message: str
	
