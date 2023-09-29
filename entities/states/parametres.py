from aiogram.dispatcher.filters.state import State, StatesGroup



class Limits(StatesGroup):
	limits = State()



class Spread(StatesGroup):
	spread = State()
