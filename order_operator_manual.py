import ccxt
import duckdb
import datetime
import json
from decimal import Decimal
import os
# Replace these with your actual Indodax API key and secret
api_key = os.getenv("indodax_api_key")
secret_key = os.getenv("indodax_secret_key")

# Create an instance of the Indodax exchange with your credentials
exchange = ccxt.indodax({
    'apiKey': api_key,
    'secret': secret_key,
})

# Load market information
exchange.load_markets()

def execute_trade_based_on_signal(ammount,price,typests):
    try:
        # Define the trading pair
        symbol = 'BTC/IDR'

        price_limit_str = str(price)
        price_limit = float(price_limit_str.replace(',', '')) if price_limit_str else None

            # take_profit = float(signal_data.get('take_profit')) if signal_data.get('take_profit') else None
        ticker = exchange.fetch_ticker(symbol)
        result = ammount  # Example IDR amount for trade (replace with actual logic)

        trade_amount = Decimal(result) / Decimal(price_limit)
# 0.00000936 BTC
        print(typests)
        print(Decimal(trade_amount))
        print(Decimal(price_limit))
        # print(typests)
        order = exchange.create_order(symbol, 'limit', typests, Decimal(str(trade_amount)[:9]),Decimal(price_limit))
        print(f"Market buy order executed: {order}")
        print(order)
    except ccxt.InsufficientFunds as e:
        print("Insufficient funds: Please make sure you have enough balance in your wallet.")
    except ccxt.AuthenticationError as e:
        print("Authentication failed: Please check your API key and secret.")

# if __name__ == "__main__":
    # loss = exchange.fetch
    # Fetch the ticker for BTC/IDR
ticker = exchange.fetch_ticker('BTC/IDR')

# Get the last price
last_price = ticker['last']
ammount = 100000
price = last_price
print(f"Last price of BTC/IDR: {last_price} IDR")
execute_trade_based_on_signal(ammount,price,typests = 'sell')











# # Create an instance of the Indodax exchange with your credentials
# exchange = ccxt.indodax({
#     'apiKey': api_key,
#     'secret': secret_key,
# })

# # Load market information
# exchange.load_markets()

# # Create or connect to the DuckDB database
# db_connection = duckdb.connect('trade_history.db')

# # Create a table to store the order history if it doesn't exist
# db_connection.execute('''
# CREATE TABLE IF NOT EXISTS order_history (
#     order_id TEXT,
#     timestamp TEXT,
#     symbol TEXT,
#     side TEXT,
#     order_type TEXT,
#     amount REAL,
#     price REAL,
#     status TEXT
# )
# ''')

# def execute_trade_based_on_signal(signal_json):
#     """
#     Executes a trade on Indodax based on the signal data in JSON format.
#     Saves the trade details into a DuckDB database.

#     :param signal_json: JSON string containing trade signal information.
#     """
#     try:
#         # Parse the JSON string to a Python dictionary
#         signal_data = json.loads(signal_json)

#         # Define the trading pair
#         symbol = 'BTC/IDR'

#         # Get the type of price order and limit price from the signal
#         price_order = signal_data.get('price_order')
#         price_limit_str = signal_data.get('price_limit_order')
#         price_limit = float(price_limit_str.replace(',', '')) if price_limit_str else None

#         # Step 1: Fetch current market price to calculate trade amount in BTC
#         ticker = exchange.fetch_ticker(symbol)
#         # current_price = ticker['last']
#         # current_price = Decimal(str(ticker['last']))
#         # rp_amount = Decimal('11000')
        
#         # Step 3: Calculate the amount of BTC to buy/sell with the given IDR amount
#         # trade_amount = rp_amount / current_price
#         # trade_amount = float(trade_amount.quantize(Decimal('1.00000000')))  # 8 decimal places

#         # Ensure the amount in IDR is not below the minimum threshold set by Indodax
        
#         # trade_amount = rp_amount
#         # trade_amount = float(f"{trade_amount:.8f}")
#         # print(rp_amount)
#         # print(trade_amount)
#         # print(Decimal(trade_amount))
#         # print(price_limit)
#         # trade_amount = 0.01
#         # result = str(price_limit)[:5]
#         result = 11000

#         # value = 1045500

#         trade_amount =  float(result)/price_limit

#         # Execute corresponding trade action using exchange.create_order()
#         order = None
#         if price_order == 'market_buy':
#             # Execute a market buy order
#             # print(symbol)
#             # print(trade_amount)
#             order = exchange.create_order(symbol, 'limit', 'buy', Decimal(trade_amount),Decimal(price_limit))
#             print(f"Limit buy order executed at {price_limit}: {order}")
#             # print(f"Market buy order executed: {order}")
#             print(f"Market buy order executed:")

#         elif price_order == 'market_sell':
#             # Execute a market sell order
#             order = exchange.create_order(symbol, 'limit', 'sell', Decimal(trade_amount),Decimal(price_limit))
#             print(f"Limit sell order executed at {price_limit}: {order}")
#             # print(f"Market sell order executed: {order}")
#             print(f"Market sell order executed: ")

#         elif price_order == 'buy_limit' and price_limit is not None:
#             # Execute a limit buy order at the specified price
#             order = exchange.create_order(symbol, 'limit', 'buy', Decimal(trade_amount), Decimal(price_limit))
#             print(f"Limit buy order executed at {price_limit}: {order}")
#             print(f"Limit buy order executed at {price_limit}: ")

#         elif price_order == 'sell_limit' and price_limit is not None:
#             # Execute a limit sell order at the specified price
#             order = exchange.create_order(symbol, 'limit', 'sell', Decimal(trade_amount), Decimal(price_limit))
#             print(f"Limit sell order executed at {price_limit}: {order}")
#             print(f"Limit sell order executed at {price_limit}:")

#         else:
#             print(f"Invalid or unsupported price order type: {price_order}")

#         # Save the order to DuckDB if executed
#         if order:
#             save_order_to_duckdb(order)

#     except ccxt.InsufficientFunds as e:
#         print("Insufficient funds: Please make sure you have enough balance in your wallet.")
#     except ccxt.AuthenticationError as e:
#         print("Authentication failed: Please check your API key and secret.")
#     except Exception as e:
#         raise
#         print(f"An error occurred: {e}")

# def save_order_to_duckdb(order):
#     """
#     Saves order details to the DuckDB database.

#     :param order: Order object returned from the exchange
#     """
#     # Extract order details
#     order_id = order.get('id', '')
#     timestamp = datetime.datetime.now().isoformat()
#     symbol = order.get('symbol', '')
#     side = order.get('side', '')
#     order_type = order.get('type', '')
#     amount = order.get('amount', 0.0)
#     price = order.get('price', 0.0)
#     status = order.get('status', '')

#     # Insert order details into the DuckDB database
#     db_connection.execute('''
#         INSERT INTO order_history (
#             order_id, timestamp, symbol, side, order_type, amount, price, status
#         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (order_id, timestamp, symbol, side, order_type, amount, price, status))

#     print(f"Order saved to DuckDB: {order_id}")

# # Example JSON response data for the trade signal
# response_json = '''
# {
#     "status": "buy",
#     "risk": "1.5%",
#     "confident": "80%",
#     "indicator": {
#         "parabolic_sar": "80%",
#         "ema_crossover": "75%",
#         "vwap": "70%",
#         "stochastic": "60%",
#         "rsi": "50%",
#         "bollinger_bands": "40%",
#         "macd": "80%",
#         "50_sma": "70%"
#     },
#     "price_order": "market_buy",
#     "price_limit_order": "1,045,500",
#     "desc": "The analysis shows strong bullish momentum with Parabolic SAR, MACD, and EMA indicators confirming an uptrend. Stochastic and RSI suggest potential for upward movement, while price is above VWAP and 50 SMA, indicating buying pressure."
# }
# '''

# # Example usage
# if __name__ == "__main__":
#     execute_trade_based_on_signal(response_json)
