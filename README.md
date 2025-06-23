# V20 Stock Trading Strategy Backtester

This repository contains a Python script designed to backtest the "V20" stock trading strategy on historical daily candlestick data. The script is optimized for use in Google Colab, leveraging Google Drive for file storage and Plotly for generating interactive trade visualizations.

It systematically analyzes multiple lists of stocks, applies a specific pattern-based trading logic, and generates detailed reports on both **completed trades** (realized profit/loss) and **open trades** (unrealized profit/loss as of the backtest end date).

## Key Features

* **Core V20 Strategy:** Identifies setups based on a strong upward momentum (>20% gain in a series of green candles) and trades the subsequent retracement.
* **Batch Processing:** Iterates through multiple source files (`v40_token.csv`, `v40next_token.csv`, `v200_token.csv`) to test the strategy against different stock universes.
* **Advanced Rules Engine:**
    * **V200 SMA Filter:** Applies a 200-day Simple Moving Average (SMA) filter for stocks in the `v200_token.csv` list, ensuring buys occur below this key technical level.
    * **Pyramiding/Re-investment:** Allows for a single, slightly larger re-investment in a stock from the V40 lists if a second opportunity arises.
* **Interactive Visualizations:** Automatically generates a Plotly candlestick chart for every completed trade, visually mapping the setup period, entry/exit points, and key price levels.
* **Comprehensive Reporting:** Produces two distinct CSV reports:
    1.  `completed_trades_summary_v20.csv`: A detailed log of all trades that were successfully entered and exited.
    2.  `open_trades_summary_v20.csv`: A snapshot of all trades that were entered but had not hit their sell target by the end of the historical data period.

## The V20 Trading Strategy

The strategy is executed based on a clear, four-step mechanical process:

1.  **Setup Identification:** The script scans for a group of continuous green candles (where `close > open`). This group only qualifies as a setup if the price gain from the period's lowest low to its highest high exceeds **20%**.
2.  **Range Definition:** Once a valid setup is found, a trading range is defined by its `lowest_low` (the entry level) and its `highest_high` (the exit target).
3.  **Buy Execution:** After the setup period, the script waits for the price to retrace. A **buy** order is triggered the first time the daily low touches or drops below the `lowest_low` of the setup range.
4.  **Sell Execution:** After a position is entered, a **sell** order is triggered the first time the daily high touches or exceeds the `highest_high` of the setup range.

## Prerequisites & Setup

* A Google Account (for Google Drive and Google Colab).
* Python 3 environment (provided by Google Colab).
* Required Python libraries: `pandas` and `plotly`. The script assumes these are available in the Colab environment.

## Required File Structure

For the script to run correctly, you **must** organize your files on Google Drive exactly as shown below.


Certainly. It seems the previous response was cut off. My apologies for that.

Here is the complete README.md content in raw Markdown format for you to copy and paste.

Markdown

# V20 Stock Trading Strategy Backtester

This repository contains a Python script designed to backtest the "V20" stock trading strategy on historical daily candlestick data. The script is optimized for use in Google Colab, leveraging Google Drive for file storage and Plotly for generating interactive trade visualizations.

It systematically analyzes multiple lists of stocks, applies a specific pattern-based trading logic, and generates detailed reports on both **completed trades** (realized profit/loss) and **open trades** (unrealized profit/loss as of the backtest end date).

## Key Features

* **Core V20 Strategy:** Identifies setups based on a strong upward momentum (>20% gain in a series of green candles) and trades the subsequent retracement.
* **Batch Processing:** Iterates through multiple source files (`v40_token.csv`, `v40next_token.csv`, `v200_token.csv`) to test the strategy against different stock universes.
* **Advanced Rules Engine:**
    * **V200 SMA Filter:** Applies a 200-day Simple Moving Average (SMA) filter for stocks in the `v200_token.csv` list, ensuring buys occur below this key technical level.
    * **Pyramiding/Re-investment:** Allows for a single, slightly larger re-investment in a stock from the V40 lists if a second opportunity arises.
* **Interactive Visualizations:** Automatically generates a Plotly candlestick chart for every completed trade, visually mapping the setup period, entry/exit points, and key price levels.
* **Comprehensive Reporting:** Produces two distinct CSV reports:
    1.  `completed_trades_summary_v20.csv`: A detailed log of all trades that were successfully entered and exited.
    2.  `open_trades_summary_v20.csv`: A snapshot of all trades that were entered but had not hit their sell target by the end of the historical data period.

## The V20 Trading Strategy

The strategy is executed based on a clear, four-step mechanical process:

1.  **Setup Identification:** The script scans for a group of continuous green candles (where `close > open`). This group only qualifies as a setup if the price gain from the period's lowest low to its highest high exceeds **20%**.
2.  **Range Definition:** Once a valid setup is found, a trading range is defined by its `lowest_low` (the entry level) and its `highest_high` (the exit target).
3.  **Buy Execution:** After the setup period, the script waits for the price to retrace. A **buy** order is triggered the first time the daily low touches or drops below the `lowest_low` of the setup range.
4.  **Sell Execution:** After a position is entered, a **sell** order is triggered the first time the daily high touches or exceeds the `highest_high` of the setup range.

## Prerequisites & Setup

* A Google Account (for Google Drive and Google Colab).
* Python 3 environment (provided by Google Colab).
* Required Python libraries: `pandas` and `plotly`. The script assumes these are available in the Colab environment.

## Required File Structure

For the script to run correctly, you **must** organize your files on Google Drive exactly as shown below.

```text

/content/drive/My Drive/
└── stock_data/
├── 2025-06-17/                 &lt;-- Your data folder, name must match DATA_FOLDER_DATE
│   ├── ASIANPAINT-EQ.csv
│   ├── RELIANCE-EQ.csv
│   └── ... (all other stock data CSVs for the backtest)
│
├── v40_token.csv               &lt;-- Stock list file 1
├── v40next_token.csv           &lt;-- Stock list file 2
└── v200_token.csv              &lt;-- Stock list file 3

```

**Important Notes:**

* **Historical Data CSVs:** Each stock's data file (e.g., `ASIANPAINT-EQ.csv`) must contain the columns: `timestamp`, `open`, `high`, `low`, `close`.
* **Stock List CSVs:** Each token list file (e.g., `v40_token.csv`) must contain a column named `ticker` that lists the corresponding stock data filenames.

## How to Run the Backtest

1.  **Organize Files:** Ensure your data files and stock lists are arranged in your Google Drive according to the structure described above.
2.  **Open in Colab:** Upload or paste the Python script into a new Google Colab notebook.
3.  **Configure Variables:** Review the variables in the "INPUT VARIABLES" section at the top of the script and adjust if necessary (e.g., `DATA_FOLDER_DATE`, `CAPITAL_PER_TRADE`).
4.  **Execute Script:** Run all cells in the notebook (`Runtime` -> `Run all`).
5.  **Authorize Drive:** When prompted, grant the notebook permission to access your Google Drive files.
6.  **Analyze Results:** The script will print its progress. Upon completion, it will display summary tables in the output and save the detailed CSV reports to your `stock_data` folder on Google Drive.

## Understanding the Output

The script provides results in three primary ways:

1.  **Console Logs:** Real-time updates on which stock list and which individual stock is being processed, along with success or failure messages for finding trades.
2.  **Interactive Charts:** For every *completed* trade, a rich, interactive chart will be displayed directly in the Colab output, allowing you to visually inspect the trade.
3.  **CSV Reports:** Two detailed CSV files are saved to your Google Drive:
    * `completed_trades_summary_v20.csv`: Contains one row for each completed trade, with columns for entry/exit dates and prices, investment, and realized profit/loss.
    * `open_trades_summary_v20.csv`: Contains one row for each position that was entered but not exited. It shows the unrealized P/L based on the last known price in the dataset.

### Example CSV Output

**Completed Trades:**

| Stock       | Source File | Entry Date   | Exit Date    | Investment | Profit    | Profit % |
| :---------- | :---------- | :----------- | :----------- | :--------- | :-------- | :------- |
| RELIANCE-EQ | V40         | 2024-11-05   | 2024-12-10   | 99,980.00  | 21,420.00 | 21.42    |
| ...         | ...         | ...          | ...          | ...        | ...       | ...      |

**Open Trades:**

| Stock   | Source File | Status | Entry Date   | Target Exit Price | Unrealized P/L | Unrealized P/L % |
| :------ | :---------- | :----- | :----------- | :---------------- | :------------- | :--------------- |
| INFY-EQ | V40Next     | Open   | 2025-05-20   | 1650.50           | -4,550.00      | -4.61            |
| ...     | ...         | ...    | ...          | ...               | ...            | ...              |

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
