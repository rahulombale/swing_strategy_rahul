import pandas as pd
import plotly.graph_objects as go
from google.colab import drive
from datetime import datetime
import os

# --- 1. SETUP AND CONFIGURATION ---

# Mount Google Drive
try:
    drive.mount('/content/drive', force_remount=True)
except Exception as e:
    print(f"Could not mount drive: {e}")

# --- INPUT VARIABLES ---
DATA_FOLDER_DATE = '2025-06-17'
DATA_BASE_PATH = '/content/drive/My Drive/stock_data/'
BASE_DATA_PATH = f'{DATA_BASE_PATH}{DATA_FOLDER_DATE}/'

# --- OUTPUT FILE NAMES ---
COMPLETED_TRADES_FILE = 'completed_trades_summary_v20.csv'
OPEN_TRADES_FILE = 'open_trades_summary_v20.csv'


# Stock list configuration
STOCK_LIST_FILES = [
    'v40_token.csv',
    'v40next_token.csv',
    'v200_token.csv'
]
SOURCE_FILE_MAPPING = {
    'v40_token.csv': 'V40',
    'v40next_token.csv': 'V40Next',
    'v200_token.csv': 'V200'
}
TICKER_COLUMN_NAME = 'ticker'

# Capital and strategy parameters
CAPITAL_PER_TRADE = 100000
REINVESTMENT_INCREASE_FACTOR = 1.03
SMA_PERIOD = 200


# --- 2. CORE FUNCTIONS ---

def load_data(file_path, stock_name_for_print):
    """Loads and preprocesses stock data, including calculating the SMA."""
    if not os.path.exists(file_path):
        print(f"      - WARNING: Data file not found for {stock_name_for_print} at {file_path}. Skipping.")
        return None
    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        df[f'SMA_{SMA_PERIOD}'] = df['close'].rolling(window=SMA_PERIOD).mean()
        return df
    except Exception as e:
        print(f"      - ERROR: Could not process file for {stock_name_for_print}. Reason: {e}")
        return None

def find_v20_setups(df, pct_change_threshold=0.20, start_scan_index=0):
    """Identifies all qualifying v20 setups from a given start index."""
    setups = []
    i = start_scan_index
    while i < len(df):
        if df['close'].iloc[i] > df['open'].iloc[i]:
            start_index = i
            j = i
            while j + 1 < len(df) and df['close'].iloc[j+1] > df['open'].iloc[j+1]:
                j += 1
            end_index = j
            segment = df.iloc[start_index:end_index + 1]
            lowest_low = segment['low'].min()
            highest_high = segment['high'].max()
            if (highest_high - lowest_low) / lowest_low > pct_change_threshold:
                setups.append({
                    'start_date': segment.index[0],
                    'end_date': segment.index[-1],
                    'lowest_low': lowest_low,
                    'highest_high': highest_high,
                    'scan_from_index': end_index + 1
                })
            i = end_index + 1
        else:
            i += 1
    return setups

def execute_backtest(df, stock_name, capital, source_file_name):
    """
    Executes trades and categorizes them into 'completed' and 'open' trades.
    Returns two lists: completed_trades, open_trades.
    """
    completed_trades = []
    open_trades = []
    last_trade_end_index = 0
    trade_count_for_stock = 0
    is_v200_stock = SOURCE_FILE_MAPPING.get(source_file_name) == 'V200'
    last_available_date = df.index[-1]
    last_available_close = df['close'].iloc[-1]

    while True:
        # Enforce trade limits: 1 for V200, 2 for others
        if (is_v200_stock and trade_count_for_stock >= 1) or \
           (not is_v200_stock and trade_count_for_stock >= 2):
            break

        setups = find_v20_setups(df, start_scan_index=last_trade_end_index)
        if not setups:
            break

        trade_found_in_loop = False
        for setup in setups:
            scan_df = df.iloc[setup['scan_from_index']:]
            buy_price = setup['lowest_low']
            sell_price_target = setup['highest_high']

            entry_mask = scan_df['low'] <= buy_price
            if entry_mask.any():
                buy_signal_candle = scan_df[entry_mask].iloc[0]
                buy_date = buy_signal_candle.name

                # V200 SMA Check
                if is_v200_stock:
                    sma_at_buy = buy_signal_candle[f'SMA_{SMA_PERIOD}']
                    if pd.isna(sma_at_buy) or buy_price >= sma_at_buy:
                        continue # Skip setup if SMA condition fails

                # Determine capital for this specific trade
                current_capital = capital
                if trade_count_for_stock == 1 and not is_v200_stock:
                    current_capital *= REINVESTMENT_INCREASE_FACTOR

                num_shares = int(current_capital / buy_price)
                if num_shares == 0: continue
                investment = num_shares * buy_price

                # Now, check for an exit
                sell_scan_df = scan_df.loc[buy_date:].iloc[1:]
                exit_mask = sell_scan_df['high'] >= sell_price_target if not sell_scan_df.empty else pd.Series(False)

                if exit_mask.any():
                    # --- COMPLETED TRADE ---
                    sell_signal_candle = sell_scan_df[exit_mask].iloc[0]
                    sell_date = sell_signal_candle.name
                    sale_value = num_shares * sell_price_target
                    profit = sale_value - investment
                    profit_pct = (profit / investment) * 100 if investment > 0 else 0

                    completed_trades.append({
                        'Stock': stock_name, 'Source File': SOURCE_FILE_MAPPING.get(source_file_name),
                        'Entry Date': buy_date, 'Exit Date': sell_date,
                        'Entry Price': buy_price, 'Exit Price': sell_price_target,
                        'Investment': round(investment, 2), 'Sale Value': round(sale_value, 2),
                        'Profit': round(profit, 2), 'Profit %': round(profit_pct, 2),
                        'Setup Start': setup['start_date'], 'Setup End': setup['end_date'], 'Shares': num_shares
                    })
                    last_trade_end_index = df.index.get_loc(sell_date) + 1
                else:
                    # --- OPEN TRADE ---
                    unrealized_pnl = (last_available_close - buy_price) * num_shares
                    unrealized_pnl_pct = (unrealized_pnl / investment) * 100 if investment > 0 else 0
                    open_trades.append({
                        'Stock': stock_name, 'Source File': SOURCE_FILE_MAPPING.get(source_file_name),
                        'Status': 'Open', 'Entry Date': buy_date,
                        'Entry Price': buy_price, 'Target Exit Price': sell_price_target,
                        'Investment': round(investment, 2),
                        'Last Known Date': last_available_date,
                        'Last Price': round(last_available_close, 2),
                        'Unrealized P/L': round(unrealized_pnl, 2),
                        'Unrealized P/L %': round(unrealized_pnl_pct, 2), 'Shares': num_shares
                    })
                    # Since a position is open, we stop processing this stock
                    last_trade_end_index = len(df)

                trade_count_for_stock += 1
                trade_found_in_loop = True
                break # Move to the next stock/re-investment check

        if not trade_found_in_loop:
            break # No more actionable setups found, exit while loop

    return completed_trades, open_trades


def plot_trade(df, trade):
    """Generates an interactive candlestick chart for a single COMPLETED trade."""
    # This function remains unchanged and is only called for completed trades.
    plot_start = trade['Setup Start'] - pd.Timedelta(days=20)
    plot_end = trade['Exit Date'] + pd.Timedelta(days=20)
    chart_df = df.loc[plot_start:plot_end]
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=chart_df.index,
                                  open=chart_df['open'], high=chart_df['high'],
                                  low=chart_df['low'], close=chart_df['close'],
                                  name=trade['Stock']))
    if trade['Source File'] == 'V200':
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df[f'SMA_{SMA_PERIOD}'],
                                 mode='lines', name=f'{SMA_PERIOD}-day SMA',
                                 line=dict(color='cyan', width=1)))
    fig.add_hline(y=trade['Entry Price'], line_dash="dash", line_color="springgreen",
                  annotation_text=f"Buy Level: {trade['Entry Price']:.2f}",
                  annotation_position="bottom right")
    fig.add_hline(y=trade['Exit Price'], line_dash="dash", line_color="red",
                  annotation_text=f"Sell Target: {trade['Exit Price']:.2f}",
                  annotation_position="top right")
    fig.add_vrect(x0=trade['Setup Start'], x1=trade['Setup End'],
                  fillcolor="rgba(255, 255, 0, 0.15)", layer="below", line_width=0,
                  annotation_text="Setup", annotation_position="top left")
    fig.add_trace(go.Scatter(
        x=[trade['Entry Date'], trade['Exit Date']], y=[trade['Entry Price'], trade['Exit Price']],
        mode='markers', marker=dict(color=['springgreen', 'red'], size=14, symbol=['triangle-up', 'triangle-down'],
                                     line=dict(width=2, color='white')), name='Trade Points'))
    fig.update_layout(
        title=f"V20 Trade: {trade['Stock']} ({trade['Source File']}) | {trade['Entry Date'].date()} to {trade['Exit Date'].date()}",
        xaxis_title="Date", yaxis_title="Price (INR)", xaxis_rangeslider_visible=False,
        template="plotly_dark", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig.show()


# --- 3. MAIN EXECUTION BLOCK ---

if __name__ == '__main__':
    all_completed_trades = []
    all_open_trades = []

    print("--- Starting Enhanced V20 Strategy Batch Backtest ---")
    print("Now tracking both COMPLETED and OPEN trades.")

    for list_file_name in STOCK_LIST_FILES:
        stock_list_path = os.path.join(DATA_BASE_PATH, list_file_name)
        print(f"\n[1] Processing stock list: {list_file_name}")
        try:
            stocks_df = pd.read_csv(stock_list_path)
            tickers = stocks_df[TICKER_COLUMN_NAME].dropna().unique()
            print(f"    - Found {len(tickers)} unique stocks.")

            for ticker in tickers:
                print(f"  [2] Analyzing stock: {ticker}")
                data_file_path = f"{BASE_DATA_PATH}{ticker}.csv"
                df = load_data(data_file_path, ticker)

                if df is not None:
                    completed, opened = execute_backtest(df, ticker, CAPITAL_PER_TRADE, list_file_name)
                    if completed:
                        print(f"      - SUCCESS: Found {len(completed)} completed trade(s).")
                        all_completed_trades.extend(completed)
                        for trade in completed:
                            plot_trade(df, trade)
                    if opened:
                        print(f"      - NOTE: Found {len(opened)} open trade(s) (target not met).")
                        all_open_trades.extend(opened)
                    if not completed and not opened:
                        print("      - No trades triggered from setups.")

        except FileNotFoundError:
            print(f"    - ERROR: Stock list file not found at {stock_list_path}. Skipping.")
        except Exception as e:
            print(f"    - An unexpected error occurred while processing {list_file_name}: {e}")

    # --- 4. FINAL SUMMARY AND OUTPUT ---
    print("\n" + "="*82)
    print("--- BACKTESTING COMPLETE: FINAL SUMMARY ---")
    print("="*82)

    # --- COMPLETED TRADES SUMMARY ---
    if all_completed_trades:
        completed_df = pd.DataFrame(all_completed_trades)
        cols_order = ['Stock', 'Source File', 'Entry Date', 'Exit Date', 'Entry Price',
                    'Exit Price', 'Investment', 'Sale Value', 'Profit', 'Profit %',
                    'Setup Start', 'Setup End', 'Shares']
        completed_df = completed_df[cols_order]
        output_path = os.path.join(DATA_BASE_PATH, COMPLETED_TRADES_FILE)
        completed_df.to_csv(output_path, index=False)

        print(f"\nSUCCESS: Completed trades summary saved to '{output_path}'")
        print("\n" + "="*28 + " COMPLETED TRADES SUMMARY " + "="*28)
        print(completed_df.to_string())
        print("="*82)

        # Performance Metrics for Completed Trades
        total_profit = completed_df['Profit'].sum()
        total_investment = completed_df['Investment'].sum()
        num_trades = len(completed_df)
        win_rate = (len(completed_df[completed_df['Profit'] > 0]) / num_trades) * 100 if num_trades > 0 else 0
        print("\n--- PERFORMANCE METRICS (Completed Trades Only) ---")
        print(f"Total Completed Trades: {num_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Total Realized Profit/Loss: ₹{total_profit:,.2f}")
        if total_investment > 0:
            roi = (total_profit / total_investment) * 100
            print(f"Return on Deployed Capital (Realized): {roi:.2f}%")

    else:
        print("\nNo completed trades were found across any stocks.")

    # --- OPEN TRADES SUMMARY ---
    if all_open_trades:
        open_df = pd.DataFrame(all_open_trades)
        cols_order = ['Stock', 'Source File', 'Status', 'Entry Date', 'Entry Price',
                    'Target Exit Price', 'Investment', 'Last Known Date', 'Last Price',
                    'Unrealized P/L', 'Unrealized P/L %', 'Shares']
        open_df = open_df[cols_order]
        output_path = os.path.join(DATA_BASE_PATH, OPEN_TRADES_FILE)
        open_df.to_csv(output_path, index=False)

        print(f"\nSUCCESS: Open trades summary saved to '{output_path}'")
        print("\n" + "="*24 + " OPEN TRADES (TARGET NOT MET) SUMMARY " + "="*23)
        print(open_df.to_string())
        print("="*82)

        # Performance Metrics for Open Trades
        total_unrealized_pnl = open_df['Unrealized P/L'].sum()
        print("\n--- METRICS (Open Trades Only) ---")
        print(f"Total Open Positions: {len(open_df)}")
        # --- FIX IS ON THE NEXT LINE ---
        # The variable 'last_available_date' is not available here.
        # We use the global 'DATA_FOLDER_DATE' which represents the backtest's end date.
        print(f"Total Unrealized P/L as of {DATA_FOLDER_DATE}: ₹{total_unrealized_pnl:,.2f}")

    else:
        print("\nNo open trades were found at the end of the backtest period.")
