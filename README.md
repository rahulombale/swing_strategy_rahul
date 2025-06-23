# Python-Based Stock Trading Strategy Backtester

This repository contains Python scripts designed to backtest distinct quantitative trading strategies on historical stock data. The scripts are built using `pandas` for data manipulation and `plotly` for interactive charting, all within the Google Colab environment.

Each script is a self-contained backtesting engine capable of processing lists of stocks, applying a specific set of rules, and generating detailed reports on trade performance.

## Strategies Implemented

This repository includes backtesters for the following two strategies:

1.  **V20 Momentum Strategy**
2.  **Moving Average Contrarian Strategy**

---

### 1. V20 Momentum Strategy

This is a momentum-based, swing trading strategy that aims to capitalize on strong upward thrusts and subsequent retracements.

#### **Strategy Logic**

1.  **Setup:** Identifies a sequence of continuous green candles where the price gain from the period's lowest low to its highest high exceeds **20%**.
2.  **Range:** Defines a trading range based on the setup's `lowest_low` (buy level) and `highest_high` (sell target).
3.  **Buy Signal:** Triggers a buy order when the price retraces and touches the `lowest_low` after the setup is complete.
4.  **Sell Signal:** Triggers a sell order when the price rallies and touches the `highest_high` after the position is entered.

#### **Special Rules**
* **Stock Universes:** Applicable to `v40_token.csv`, `v40next_token.csv`, and `v200_token.csv`.
* **V200 Filter:** For stocks from the `v200` list, the buy signal is only valid if the entry price is also below the 200-day SMA.
* **Pyramiding:** For `v40` and `v40next` stocks, allows for **one** additional re-investment with 3% more capital if a second, distinct setup occurs after a trade is completed.

---

### 2. Moving Average Contrarian Strategy

This is a contrarian, trend-following strategy designed to buy into extreme pessimism and sell into extreme optimism, based on the alignment of key moving averages.

#### **Strategy Logic**

1.  **Philosophy:** Buys when short, mid, and long-term traders are theoretically at a loss. Sells when all are in profit.
2.  **Buy Signal:** Triggers a buy order on the next day's open when the previous day's close satisfies the condition: `Close < 20 SMA < 50 SMA < 200 SMA`.
3.  **Sell Signal:** Triggers a sell order on the next day's open when the previous day's close satisfies the condition: `Close > 20 SMA > 50 SMA > 200 SMA`.

#### **Special Rules**
* **Stock Universe:** Applicable **only** to stocks from `v40_token.csv`.
* **Averaging Down:** If in a position, allows for **one** additional buy (averaging down) if the price drops 10% below the initial entry price. This is preferred over taking a new trade.
* **Chart Colors:** Plots use Green (20 SMA), Red (50 SMA), and Black (200 SMA).

---

## Common Features & Architecture

Both scripts share a common set of features and operating requirements.

* **Google Colab & Drive:** Designed to run in Google Colab, using Google Drive for file I/O.
* **Batch & Single-Stock Mode:** A simple boolean toggle (`RUN_SINGLE_STOCK`) at the top of the main execution block allows you to switch modes:
    * `True`: Runs the backtest for one specified stock and generates a detailed Plotly chart. Ideal for debugging and deep-dives.
    * `False`: Runs the backtest for all stocks in the relevant source file(s). Ideal for generating aggregate performance statistics.
* **Comprehensive Reporting:** Both scripts track and report two categories of trades:
    1.  **Completed Trades:** Trades that have been both entered and exited.
    2.  **Open Trades:** Positions that were entered but had not hit their sell condition by the end of the data period.
* **CSV Output:** The results are saved into two separate `.csv` files for easy analysis (`completed_trades...` and `open_trades...`).

## Required File Structure

For the scripts to run, your files **must** be organized on Google Drive as follows:

```text
/content/drive/My Drive/
└── stock_data/
├── 2025-06-17/                 &lt;-- Data folder, name must match DATA_FOLDER_DATE
│   ├── ASIANPAINT-EQ.csv
│   ├── RELIANCE-EQ.csv
│   └── ... (all other stock data CSVs)
│
├── v40_token.csv               &lt;-- Stock list file 1
├── v40next_token.csv           &lt;-- Stock list file 2
└── v200_token.csv              &lt;-- Stock list file 3
```

## How to Use

1.  **Organize Files:** Ensure your data and stock lists are in your Google Drive as per the structure above.
2.  **Open in Colab:** Open the desired strategy script (`V20_Strategy.ipynb` or `MA_Strategy.ipynb`) in Google Colab.
3.  **Select Mode:** In the main execution block, set the `RUN_SINGLE_STOCK` toggle to `True` or `False`. If `True`, specify the `TICKER_TO_TEST`.
4.  **Run Script:** Execute all cells (`Runtime` -> `Run all`).
5.  **Authorize Drive:** Grant the notebook permission to access your Google Drive when prompted.
6.  **Analyze Results:** Review the output in the Colab console. The final summary tables will be printed, and the full CSV reports will be saved to your `stock_data` folder on Google Drive. If in single-stock mode, an interactive chart will also be displayed.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
