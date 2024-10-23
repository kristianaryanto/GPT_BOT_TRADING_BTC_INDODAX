import ccxt
import os
# Replace these with your actual Indodax API key and secret
api_key = os.getenv("indodax_api_key")
secret_key = os.getenv("indodax_secret_key")

# Create an instance of the Indodax exchange
exchange = ccxt.indodax({
    'apiKey': api_key,
    'secret': secret_key,
})

# Load markets - recommended to refresh available markets
exchange.load_markets()

ticker = exchange.fetch_ticker('BTC/IDR')

# Extract the current price (last price)
btc_to_idr_price = ticker['last']

# Fetch the balance for your wallet
try:
    balance = exchange.fetch_balance()
    print('Wallet Balances:')

    # Print balance for each asset
    for currency, info in balance['total'].items():
        if info > 0:  # Only display assets that have a non-zero balance
            print(f"{currency}: {info}")
            if currency == "BTC":
                amount_in_idr = float(info) * float(btc_to_idr_price)
                print(f"asset btc dalam {amount_in_idr}")
except ccxt.AuthenticationError as e:
    print("Authentication failed: Please check your API key and secret.")
except Exception as e:
    print(f"An error occurred: {e}")