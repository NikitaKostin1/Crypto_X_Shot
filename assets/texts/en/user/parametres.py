signals_type_option = """
Select the trade type
"""


parametres = """ \
<b>Crypto Shot</b> settings:

• <b>Limits:</b> {limits}
• <b>Payment systems:</b> {banks}
• <b>Cryptocurrencies:</b> {currencies}
• <b>Selected exchanges:</b> {markets}
• <b>Signals with spread:</b> >{spread}%
• <b>Trading type:</b> {bid_type} - {ask_type}
• <b>Fiat currency:</b> {fiat}

We would like to draw your attention - the result of the work DEPENDS DIRECTLY on the settings of <b>Crypto Shot</b>!

To edit, click 👇
"""

any_limits = "Any"
tester_restriction = """
You’re on trial mode!
"""
tester_limits_restriction = """
You aren't available to edit this parameter!
"""
tester_currencies_restriction = """
You aren't available to edit this parameter!
"""
tester_markets_restriction = """
You aren't available to edit this parameter!
"""
tester_spread_restriction = """
Your spread cannot be higher than 1.0%
"""
tester_bid_ask_restriction = """
You only have Taker - Maker position available!
"""



limits_info = """ 
Enter the amount of the bank with which you are ready to work:
<code>For "any" amount enter 0</code>
"""
limits_type_error = """
The input is wrong!
You can enter only integers, example:
<code>15 000</code> | <code>10000</code> | <code>25000</code>
"""
limits_min_error = """
The minimum limits are {limits}, with the settings below you will not find the bundles.
"""
limits_max_error = """
The maximum amount of the pot is {limits}, with the settings above you will not find the bundles.
"""

banks_info = """
Choose the right banks for you: 
• {banks}
"""

currencies_info = """
Choose the appropriate cryptocurrencies for you:
• {currencies}
"""

markets_info = """
Choose the appropriate crypto exchanges for you 
• {markets}
"""

spread_info = """ 
Enter the spread above which you want to receive notifications:
"""
spread_type_error = """
The input is wrong!
You can enter only integers and fractional numbers, example:
<code>0.75</code> | <code>2</code> | <code>3.1</code>
"""
spread_min_error = """
Minimum spread is 0.5%, with settings below too many bindings.
"""
spread_max_error = """
The maximum spread is 5%, with the settings above you will not find the bundles.
"""

trading_type_info = """
Choose the appropriate type of transaction for you: 
• {bid_type} - {ask_type}
"""

fiat_info = """
Choose a fiat currency suitable for you: 
• {fiat}
"""

