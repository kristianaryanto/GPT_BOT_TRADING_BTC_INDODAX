import tiktoken
import logging
import openai
from textwrap import dedent
import pandas as pd
import ccxt
from finta import TA
from datetime import datetime
import numpy as np
import json
import duckdb

# Database Connection
conn = duckdb.connect('prompts_database.db')

# Constants
SYMBOL = 'BTC/IDR'
TIMEFRAME = '1h'
HISTORY_PERIOD = 31 * 24 * 60 * 60 * 1000  # 31 days in milliseconds
MAX_LIMIT = 1000

# Logging Configuration
logging.basicConfig(level=logging.INFO)

def get_exchange():
    return ccxt.indodax()

def fetch_historical_data(exchange, symbol, timeframe, history_period):
    """
    Fetch historical OHLCV data from the exchange.
    """
    now = exchange.milliseconds()
    start_time = now - history_period
    all_data = []

    while start_time < now:
        try:
            data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=start_time, limit=MAX_LIMIT)
            all_data += data
            if len(data) < MAX_LIMIT:
                break
            start_time = data[-1][0] + 1  # Move to the next batch
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            break
    
    return all_data

def calculate_technical_indicators(df):
    """
    Calculate various technical indicators and add them to the dataframe.
    """
    # RSI
    df['rsi'] = TA.RSI(df)
    
    # EMA and SMA
    df['ema_14'] = TA.EMA(df, period=14)
    df['sma_20'] = TA.SMA(df, period=20)
    
    # MACD
    macd = TA.MACD(df)
    df['macd'] = macd['MACD']
    df['macd_signal'] = macd['SIGNAL']
    
    # Bollinger Bands
    bb = TA.BBANDS(df)
    df['bb_upper'] = bb['BB_UPPER']
    df['bb_middle'] = bb['BB_MIDDLE']
    df['bb_lower'] = bb['BB_LOWER']
    
    # VWAP
    df['vwap'] = TA.VWAP(df)
    
    # Parabolic SAR
    df['psar'] = calculate_parabolic_sar(df)
    
    # Stochastic Oscillator
    df['stoch_k'], df['stoch_d'] = calculate_stochastic_oscillator(df)
    
    # Fibonacci Retracement Levels
    calculate_fibonacci_retracement(df)
    
    return df

def calculate_parabolic_sar(df, af=0.02, max_af=0.2):
    """
    Manually calculate the Parabolic SAR.
    """
    high, low, close = df['high'], df['low'], df['close']
    psar = np.zeros(len(close))
    bull = True
    ep = low[0]
    sar = high[0]

    for i in range(1, len(close)):
        prior_sar = sar
        sar = prior_sar + af * (ep - prior_sar)

        if bull:
            if low[i] < sar:
                bull = False
                sar = ep
                ep = low[i]
                af = 0.02
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + 0.02, max_af)
        else:
            if high[i] > sar:
                bull = True
                sar = ep
                ep = high[i]
                af = 0.02
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + 0.02, max_af)

        psar[i] = sar

    return psar

def calculate_stochastic_oscillator(df, period=14):
    """
    Calculate the Stochastic Oscillator.
    """
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min)
    stoch_d = stoch_k.rolling(window=3).mean()
    return stoch_k, stoch_d

def calculate_fibonacci_retracement(df):
    """
    Calculate full Fibonacci retracement and extension levels.
    """
    # Calculate the high and low prices over the entire period
    high_price = df['high'].max()
    low_price = df['low'].min()

    # Define retracement levels (common Fibonacci levels)
    fib_levels = {
        'fib_0.236': low_price + (high_price - low_price) * 0.236,
        'fib_0.382': low_price + (high_price - low_price) * 0.382,
        'fib_0.500': low_price + (high_price - low_price) * 0.5,
        'fib_0.618': low_price + (high_price - low_price) * 0.618,
        'fib_0.786': low_price + (high_price - low_price) * 0.786,
        'fib_1.000': high_price  # Full retracement level
    }

    # Define extension levels (beyond the high for projecting targets)
    extension_levels = {
        'fib_1.272': high_price + (high_price - low_price) * 0.272,
        'fib_1.618': high_price + (high_price - low_price) * 0.618,
        'fib_2.000': high_price + (high_price - low_price) * 1.0,
        'fib_2.618': high_price + (high_price - low_price) * 1.618
    }

    # Merge retracement and extension levels into one dictionary
    fib_levels.update(extension_levels)

    # Add each Fibonacci level as a new column in the DataFrame
    for level_name, level_value in fib_levels.items():
        df[level_name] = level_value

    return df

def get_openai_response(prompt: str) -> str:
    messages = [{"role": "system", "content": prompt}]
    tokens_in_messages = get_num_tokens_from_messages(
        messages=messages, model="gpt-4o-mini"
    )
    max_tokens = 8192
    tokens_for_response = max_tokens - tokens_in_messages
    print(f"tokens_in_messages: {tokens_in_messages}")
    print(f"max_tokens: {max_tokens}")
    print(f"tokens_for_response: {tokens_for_response}")
    if tokens_for_response < 200:
        return "The code file is too long to analyze. Please select a shorter file."

    logging.info("Sending request to OpenAI API for code analysis")
    logging.info("Max response tokens: %d", tokens_for_response)

    # Request completion from OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=tokens_for_response,
        n=1,
        temperature=0,
    )

    print(f"Total number of tokens used: {response['usage']['total_tokens']}")
    print(f"Number of prompt tokens: {response['usage']['prompt_tokens']}")
    print(f"Number of completion tokens: {response['usage']['completion_tokens']}")

    # print(response['choices'])
    # Return the assistant's response
    json_response_status = json_response(response)
    # print(myjson)
    full_response = response['choices'][0]['message']['content'].strip() 
    return full_response,json_response_status


def get_num_tokens_from_messages(messages, model="gpt-4o-mini"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logging.debug("Model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    # Define token costs based on model type
    if model == "gpt-3.5-turbo":
        logging.debug(
            "gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301."
        )
        return get_num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        logging.debug(
            "gpt-4 may change over time. Returning num tokens assuming gpt-4-0314."
        )
        return get_num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-4o-mini":
        # Assumed token structure for gpt-4o-mini
        tokens_per_message = 3  # Customize this based on expected behavior
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."
        )

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name

    # Assumes every conversation is primed with a start message token count
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>

    return num_tokens


def json_response(response):

    # Assuming `response` is the OpenAI response you've received
    openai_message = response['choices'][0]['message']['content'].strip()

    # Extract the JSON portion from the message content
    start_idx = openai_message.find('```json') + len('```json')
    end_idx = openai_message.find('```', start_idx)

    # Extract the JSON string
    json_string = openai_message[start_idx:end_idx].strip()

    # Convert the JSON string to a Python dictionary
    parsed_json = json.loads(json_string)

    # Print or use the parsed JSON
    # print(parsed_json)
    return parsed_json

def duck_save_prompt(prompt_full, prompt_status_json):
    """
    Save the prompt and status JSON into the DuckDB database.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS prompts (
        datetime TIMESTAMP,
        prompt_full TEXT,
        prompt_status_json TEXT
    );
    """
    conn.execute(create_table_query)

    if isinstance(prompt_status_json, dict):
        prompt_status_json = json.dumps(prompt_status_json)

    insert_query = """
    INSERT INTO prompts (datetime, prompt_full, prompt_status_json)
    VALUES (now(), ?, ?);
    """
    conn.execute(insert_query, [prompt_full, prompt_status_json])

def gpt_bot_runner():
    exchange = get_exchange()
    raw_data = fetch_historical_data(exchange, SYMBOL, TIMEFRAME, HISTORY_PERIOD)
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(raw_data, columns=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Calculate technical indicators
    df = calculate_technical_indicators(df)

    # Prepare the prompt for OpenAI
    prompt_first = dedent(f"""

You are an expert crypto trader, analyzing the market on a 1-hour timeframe using a comprehensive scalping strategy. Your analysis should include the following technical indicators: Parabolic SAR, Stochastic Oscillator, Bollinger Bands, 9-period and 21-period EMA, Relative Strength Index (RSI), Moving Average Convergence Divergence (MACD), VWAP, the 50-period Simple Moving Average (SMA), and Fibonacci retracement levels based on swing high and low. Follow these instructions carefully:
Trend Identification:

    Parabolic SAR: Identify potential trend reversals. Describe the current positioning of the Parabolic SAR dots relative to the price and whether this suggests an uptrend or downtrend.
    EMA Crossover: Confirm the trend using the 9-period EMA and 21-period EMA crossover. Determine if the EMAs show bullish (9 EMA above 21 EMA) or bearish (9 EMA below 21 EMA) momentum.
    VWAP: Assess whether the price is trading above or below VWAP to determine buying or selling pressure.
    Swing High/Low and Fibonacci: Identify the most recent significant swing high and swing low on the 1-hour chart. Draw Fibonacci retracement levels (23.6%, 38.2%, 50%, 61.8%, 78.6%) between these points to identify potential support or resistance levels. Describe how price is reacting to these levels and whether any retracement levels coincide with key support or resistance.

Entry Signal:

    Stochastic Oscillator: Assess overbought or oversold conditions (above 80 = overbought, below 20 = oversold). Use this oscillator to find long or short opportunities.
    RSI: Check for momentum by evaluating if RSI is below 30 (buying) or above 70 (selling). Note any divergence between price and RSI that may indicate reversals.
    Fibonacci Levels: Determine entry opportunities based on price reactions at key Fibonacci retracement levels. For example, consider buying near the 38.2% or 50% levels in an uptrend or selling near these levels in a downtrend.

Volatility and Reversals:

    Bollinger Bands: Gauge volatility by examining if the price touches or breaches the bands and assess the potential for reversals.
    50-period SMA: Check whether the price respects the 50-period SMA as dynamic support or resistance and assess potential for a break.

Entry Timing:

    MACD: For precision in entry, analyze the MACD line and signal line. Look for crossovers (MACD above signal = buy, MACD below signal = sell). Evaluate the histogram to gauge momentum strength and whether it is increasing or weakening.
    Fibonacci Timing: Use Fibonacci retracement levels to identify the most favorable time for entries, such as when the price approaches a retracement level and aligns with other indicators.

Exit Signal:

    Parabolic SAR: Use the Parabolic SAR dots for exit signals. If the SAR flips (dots move above or below the price), signal a trend reversal.
    Bollinger Bands/RSI: Look for reversion inside the bands or RSI moving back into neutral levels as potential exit signals.
    Fibonacci Profit Targets: Set take-profit levels at key Fibonacci retracement points (e.g., 61.8% or 78.6%). In an uptrend, consider a take-profit near the previous swing high or above the 61.8% level if momentum continues.

Risk Management:

    Set stop-loss levels based on recent support/resistance from VWAP, SMA, Bollinger Bands, or key Fibonacci levels.
    Define a strict risk-to-reward ratio, and outline a stop-loss strategy using Fibonacci retracement levels (e.g., below 23.6% for aggressive trades or below the 38.2% level for conservative trades).

Additional Fields for Limit Orders:

    Swing High/Low: Identify the most recent swing high and low to calculate potential limit orders.
    Fibonacci Retracement: Define a limit price based on the nearest Fibonacci retracement level (support for buy, resistance for sell). If buying, suggest a limit price near the nearest Fibonacci support level (38.2% or 50%). If selling, suggest a limit price near the Fibonacci resistance (61.8% or 78.6%).

Return JSON Format:

Generate a JSON response that includes the following fields:

    "status": either "buy", "wait", or "sell", based on overall market conditions and indicator alignment.
    "risk": current percentage risk level for the trade.
    "confident": confidence percentage based on indicator alignment.
    "indicator": breakdown of each indicator's contribution, including "parabolic_sar", "ema_crossover", "vwap", "stochastic", "rsi", "bollinger_bands", "macd", and "50_sma". Each should have a confidence percentage.
    "price_order": indicate "buy_limit", "sell_limit", "market_buy", "market_sell", or "wait" depending on the analysis of the indicators. Use the following logic:
        "market_buy": if the majority of indicators suggest a strong buy (bullish) trend and momentum is building.
        "market_sell": if the majority of indicators suggest a strong sell (bearish) trend and momentum is decreasing.
        "buy_limit": if a buy is suggested, but the market is near a resistance level.
        "sell_limit": if a sell is suggested, but the market is near a support level.
        "wait": if no strong signals align for either direction.
    "price_limit_order": the suggested price level to place a limit order based on the analysis of support (for buy) or resistance (for sell) with full  length price example:"1,045,500,000".
    Example logic:
        If the current price is near a support level (from VWAP, Bollinger Bands, or 50-period SMA), suggest a limit buy order slightly above this support.
        If the current price is near a resistance level (from VWAP, Bollinger Bands, or 50-period SMA), suggest a limit sell order slightly below this resistance.
    "take_profit": "suggested take-profit level based on analysis of Fibonacci retracement, support, or resistance levels (only filled if status is 'buy' or 'wait')",
    "desc": short description (max 100 words) explaining how the percentages were determined for each indicator and their combined influence on the decision.
Example Return Response:

json
{{
  "status": "buy" or "wait",
  "risk": "current percentage risk level for the trade",
  "confident": "confidence percentage based on indicator alignment",
  "indicator": {{
    "parabolic_sar": "80%",
    "ema_crossover": "70%",
    "vwap": "60%",
    "stochastic": "-50%",
    "rsi": "-50%",
    "bollinger_bands": "0%",
    "macd": "70%",
    "50_sma": "60%",
    "fibonacci": "supporting level"
}},
  "price_order": "buy_limit", "sell_limit", "market_buy", "market_sell", or "wait",
  "price_limit_order": "suggested price level for a limit order",
  "take_profit": "suggested take-profit level based on analysis of Fibonacci retracement, support, or resistance levels (only filled if status is 'buy' or 'wait')",
  "desc": "Short description of how percentages were determined and combined to influence the decision."
}}

Dataframe:
{df}

Your review:
""")

    # Get response from OpenAI
    full_response, json_response_status = get_openai_response(prompt_first)
    logging.info("Starting the hourly scheduler.")

    # Save the prompt and response
    duck_save_prompt(full_response, json_response_status)
    # print("this prompt")
    # print(json_response_status)
    # print("\n \n ")
    return(json_response_status)
    # Print saved data for verification
    # results = conn.execute("SELECT * FROM prompts").fetchall()
    # print(results)

# if __name__ == "__main__":
#     # gpt_bot_runner()
#     exchange = get_exchange()
#     raw_data = fetch_historical_data(exchange, SYMBOL, TIMEFRAME, HISTORY_PERIOD)
#     columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
#     df = pd.DataFrame(raw_data, columns=columns)
#     df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

#     # Calculate technical indicators
#     df = calculate_technical_indicators(df)
    # print(df)
