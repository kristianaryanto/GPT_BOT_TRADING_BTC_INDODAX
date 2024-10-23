# GPT_BOT_TRADING_BTC_INDODAX

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![GPT](https://img.shields.io/badge/GPT-4o--mini-blueviolet)
![Indodax](https://img.shields.io/badge/Exchange-Indodax-orange)

## 📈 Automated Bitcoin Trading Bot using GPT & Indodax

This project is an automated trading bot designed to trade Bitcoin (BTC) on the Indodax exchange using decisions made by GPT (GPT-4o-mini). It automates the trading process from data retrieval, decision making, to executing buy/sell orders. 

By leveraging AI-based decisions, this bot aims to optimize your trading performance through automated processes and strategic insights.

---

## 🚀 Features

- **AI-Powered Decisions**: Utilizes GPT to analyze market data and make trading decisions.
- **Automated Trading**: Executes buy/sell orders on the Indodax exchange based on GPT signals.
- **Future-Proof**: Currently includes take-profit strategy, with future plans to add stop loss and margin trading.

---

## 📂 Project Structure

This repository contains 3 core components:

1. **`full_bod.py`**  
   This script is the main entry point that orchestrates the entire process:
   - Cancels open orders
   - Retrieves trading decisions from GPT
   - Executes orders (buy/sell)

2. **`gpt_runner.py`**  
   Fetches market data from Indodax using a 1-hour timeframe over the last 24 hours. The data is processed, and GPT provides trading signals based on this analysis.

3. **`order_operator.py`**  
   This script is responsible for executing buy/sell orders based on GPT's signals. Currently, it implements a take-profit strategy, with future enhancements planned, such as stop-loss and margin trading.

---

## 🛠️ Installation

To get started with the project, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/GPT_BOT_TRADING_BTC_INDODAX.git
   cd GPT_BOT_TRADING_BTC_INDODAX
   ```

2. **Install dependencies**:
   Ensure you have Python 3.x installed. Then, install the required libraries using the provided `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**:  
   Make sure you set up your Indodax API keys in a secure configuration file to allow the bot to access your trading account.

---

## ⚡ Usage

Once installed, you can start the bot by running the `full_bod.py` file. The script will handle the entire process from gathering data to executing trades:

```bash
python full_bod.py
```

---

## 📊 Future Plans

- Add **Stop-Loss** functionality to minimize potential losses.
- Implement **Margin Trading** to enhance profits.
- Enable more advanced **risk management strategies**.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the project or add new features, feel free to fork the repository and submit a pull request. Please ensure your code adheres to the following guidelines:
- Clear, concise comments
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Ensure tests are passing before submitting

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgments

- Special thanks to OpenAI for GPT and to Indodax for their API.
- Inspired by the power of AI in financial markets.
```

### Key Changes:
1. The **License section** now states that the project is licensed under the Apache License 2.0.
2. The **License link** points to a `LICENSE` file in your repository, assuming you'll have one included.

This should now align better with your project's legal structure! Let me know if you need further adjustments.