from config import logger, get_conn

from entities.parametres import (
	Banks, Fiat, Markets, Currencies
)



@logger.catch
async def get_banks_by_fiat(fiat: Fiat) -> Banks:
	"""
	Retrieve a list of banks that support the specified fiat currency.

	Args:
		fiat (Fiat): The Fiat currency.

	Returns:
		Banks: A Banks object containing the list banks.
	"""
	banks = list()
	connection = await get_conn()

	records = await connection.fetch(f"""
		SELECT * 
		FROM supported_banks
		WHERE fiat = '{fiat.value.upper()}';
	""")

	for record in records:
		bank = record.get("bank")
		banks.append(bank)

	if not banks:
		logger.error(f"None banks fetched: {fiat=}")

	return Banks(banks)


@logger.catch
async def fiats_symbols() -> dict:
	"""
	Retrieve a dictionary mapping fiat currencies to their corresponding symbols.

	Returns:
		dict: A dictionary mapping fiat currencies to symbols.
	"""
	symbols = dict()
	connection = await get_conn()

	records = await connection.fetch(f"""
		SELECT fiat, fiat_symbol
		FROM supported_banks;
	""")

	for record in records:
		fiat = record.get("fiat")
		symbol = record.get("fiat_symbol")

		if not symbols.get(fiat):
			symbols[fiat] = symbol

	return symbols


@logger.catch
async def p2p_markets() -> Markets:
	"""
	Retrieve a list of only P2P markets from the database.

	Returns:
		Markets: A Markets object containing the list of P2P markets.
	"""
	markets = list()
	connection = await get_conn()

	records = await connection.fetch("""
		SELECT title
		FROM available_markets
		WHERE 
			p2p = true;
	""")
	for record in records:
		market = record.get("title")
		markets.append(market)

	return Markets(markets)


@logger.catch
async def p2p_currencies() -> Currencies:
	"""
	Retrieve a list of only P2P currencies from the database.

	Returns:
		Currencies: A Currencies object containing the list of currencies.
	"""
	currencies = list()
	connection = await get_conn()

	records = await connection.fetch("""
		SELECT title
		FROM available_currencies
		WHERE 
			p2p = true;
	""")
	for record in records:
		currency = record.get("title")
		currencies.append(currency)

	return Currencies(currencies)
