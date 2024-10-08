bot_enabled = """
Crypto Shot включён! 🟢
"""
bot_disabled = """
Crypto Shot выключен! 🔴
"""
bot_enabling_info = """
Для выключения нажмите кнопку «Вкл/Выкл»
"""
bot_disabling_info = """
Для включения нажмите кнопку «Вкл/Выкл».
"""

inefficient_parametres = """
По вашим параметрам найдено мало сигналов ❗️
Советы по параметрам:
• Добавить больше банков / бирж / криптовалюты
• Изменить лимиты (эффективнее всего на "Любые")
• Изменитe торговый фиат
"""

message = """ \
💡 <b>{bid_market} - {ask_market}</b> 💡
    • <b>{currency}</b>
    Купить: {bid_price}<code>{fiat_symbol}</code>
    Продать: {ask_price}<code>{fiat_symbol}</code>
    📈 Спред: <b>{spread}%</b>
_________________________

    ▶️ <b>Покупка</b> ▶️
    Лимиты: {bid_limits_min}{fiat_symbol} - {bid_limits_max}{fiat_symbol}
    Банк: {bid_bank}

    ◀️ <b>Продажа</b> ◀️
    Лимиты: {ask_limits_min}{fiat_symbol} - {ask_limits_max}{fiat_symbol}
    Банк: {ask_bank}
"""
