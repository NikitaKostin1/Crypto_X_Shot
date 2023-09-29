from dataclasses import dataclass
from .parsing.types import ParserResponse



@dataclass
class Signal:
	"""
	Data class representing a signal.
	"""
	message_id: int
	bid: ParserResponse
	ask: ParserResponse
