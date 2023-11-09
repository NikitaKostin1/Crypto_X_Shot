bot_enabled = """
Crypto Shot is turned on! 🟢
"""
bot_disabled = """
Crypto Shot is turned off! 🔴
"""
bot_enabling_info = """
To turn off, click «On/Off»
"""
bot_disabling_info = """
To turn on, click «On/Off»
"""

inefficient_parametres = """
Few signals were found from your parameters ❗️
Tips for options:
• Add more banks / exchanges/ cryptocurrencies
• Change limits (most effectively "Any")
• Change the Trading Fiat
"""

message = """ \
💡 <b>{bid_market} - {ask_market}</b> 💡
    • <b>{currency}</b>
    Buy: {bid_price}<code>{fiat_symbol}</code>
    Sell: {ask_price}<code>{fiat_symbol}</code>
    📈 Spread: <b>{spread}%</b>
_________________________

    ▶️ <b>Buy</b> ▶️
    Limits: {bid_limits_min}{fiat_symbol} - {bid_limits_max}{fiat_symbol}
    Bank: {bid_bank}

    ◀️ <b>Sell</b> ◀️
    Limits: {ask_limits_min}{fiat_symbol} - {ask_limits_max}{fiat_symbol}
    Bank: {ask_bank}
"""
