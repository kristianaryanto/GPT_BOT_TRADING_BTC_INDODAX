import ccxt
import duckdb
import uuid
import datetime
import json
import logging
import schedule
import time
import os
from gpt_runner import gpt_bot_runner
from order_operator import execute_trade_based_on_signal
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

def cancel_all_open_orders(symbol):
    """
    Fetches all open orders for a given symbol and cancels them.
    
    :param symbol: The trading pair symbol (e.g., 'BTC/IDR')
    """
    try:
        # Step 1: Fetch all open orders for the given symbol
        open_orders = exchange.fetch_open_orders(symbol=symbol)

        if not open_orders:
            logging.info("No open orders to cancel.")

        else:
            logging.info(f"Found {len(open_orders)} open orders. Proceeding to cancel them.")

            # Step 2: Iterate through each open order and cancel it
            for order in open_orders:
                order_id = order['id']
                logging.info(f"Cancelling order ID: {order_id}")

                # Step 3: Cancel the order by ID
                try:
                    cancel_response = exchange.cancel_order(order_id, symbol, {'side': 'buy'})
                except:
                    None
                try:
                    cancel_response = exchange.cancel_order(order_id, symbol, {'side': 'sell'})
                except:
                    None
                    
                # Print the response to confirm cancellation
                # print(f"Order ID {order_id} cancellation response: {cancel_response}")
                logging.info(f"Order ID {order_id}")


    except ccxt.AuthenticationError as e:
        logging.info("Authentication failed: Please check your API key and secret.")
    except ccxt.NetworkError as e:
        logging.info("Network error: Please check your internet connection.")
    except ccxt.BaseError as e:
        logging.info(f"An error occurred: {e}")


def run_trade_cycle():
    """
    Runs the entire trading cycle: cancels open orders and executes trades based on signals.
    """
    # Define the trading pair (e.g., BTC/IDR)
    symbol = 'BTC/IDR'

    # Step 1: Cancel all open orders for the given symbol
    logging.info(f"run cancel_all_open_orders")

    cancel_all_open_orders(symbol)
    logging.info(f"run gpt_bot_runner")

    # # Step 2: Get trading signal from GPT bot
    json_return = gpt_bot_runner()
    json_object = json.dumps(json_return)

    logging.info(f"{json_return}")
    logging.info(f"done gpt_bot_runner")

    print("\n start execution signal \n ")
    # # Step 3: Execute trade based on the provided signal
    logging.info(f"run execute_trade_based_on_signal")
    execute_trade_based_on_signal(json_object)
    logging.info(f"done execute_trade_based_on_signal")

# Schedule the trading cycle to run every hour

# Execute the trading cycle immediately
if __name__ == "__main__":
    logging.info("Starting the trading bot and executing the first trade cycle.")
    run_trade_cycle()

    # Schedule the trading cycle to run every hour
    schedule.every(1).hours.do(run_trade_cycle)

    # Run the scheduling loop with a countdown timer
    logging.info("Starting the hourly scheduler.")
    while True:
        # Check if there is a pending job to run
        schedule.run_pending()

        # Countdown until the next schedule (1 hour interval)
        next_run = schedule.next_run()
        if next_run:
            remaining_seconds = (next_run - datetime.datetime.now()).total_seconds()
            while remaining_seconds > 0:
                # logging.info(f"Time until next execution: {int(remaining_seconds // 60)} minutes, {int(remaining_seconds % 60)} seconds", end='\r')
                print(f"Time until next execution: {int(remaining_seconds // 60)} minutes, {int(remaining_seconds % 60)} seconds", end='\r')
                time.sleep(1)
                remaining_seconds -= 1