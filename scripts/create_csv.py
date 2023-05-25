import pandas as pd
import numpy as np

np.random.seed(42)  # for reproducibility


# Function to generate random dates
def random_dates(start, end, n=10):
    start_u = start.value // 10 ** 9
    end_u = end.value // 10 ** 9
    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='s')


start = pd.to_datetime('2021-01-01')
end = pd.to_datetime('2023-12-31')

data = {
    "tradeinfo_Ticker": np.random.choice(['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'], size=20),
    "tradeinfo_entry_date": random_dates(start, end, 20),
    "tradeinfo_entry_price": np.random.uniform(100, 500, size=20),
    "tradeinfo_exit_date": random_dates(start, end, 20),
    "tradeinfo_exit_price": np.random.uniform(100, 500, size=20),
    "tradeinfo_gain_percentage": np.random.uniform(-0.2, 0.2, size=20),
    "tradeinfo_gain_absolut": np.random.uniform(-100, 100, size=20),
    "tradeinfo_tax": np.random.uniform(10, 30, size=20),
    "tradeinfo_fees": np.random.uniform(1, 10, size=20),

    "fundamentals_sector": np.random.choice(
        ['Technology', 'Consumer Discretionary', 'Healthcare', 'Financials', 'Industrials'], size=20),
    "fundamentals_market_cap": np.random.uniform(10 ** 9, 10 ** 12, size=20),
    "fundamentals_price_to_earning": np.random.uniform(10, 30, size=20),
    "fundamentals_price_to_book": np.random.uniform(1, 10, size=20),
    "fundamentals_dept_to_equity": np.random.uniform(0.1, 2, size=20),
    "fundamentals_free_cash_flow": np.random.uniform(10 ** 6, 10 ** 9, size=20),
    "fundamentals_PEG_ratio": np.random.uniform(0.5, 2, size=20),
    "fundamentals_general_market_analysis": np.random.choice(['Bullish', 'Bearish', 'Neutral'], size=20),
    "fundamentals_additional_ideas": np.random.choice(['Buy', 'Sell', 'Hold'], size=20),

    "technical_RSI": np.random.uniform(0, 100, size=20),
    "technical_trend_mac_d": np.random.uniform(-5, 5, size=20),
    "technical_on_balance_volume": np.random.uniform(10 ** 6, 10 ** 9, size=20),
    "technical_AD_line": np.random.uniform(0, 1, size=20),
    "technical_ADX": np.random.uniform(0, 100, size=20),
    "technical_aroon_indicator": np.random.uniform(0, 100, size=20),

    "human_trading_idea_description": ['Idea ' + str(i) for i in range(1, 21)],
    "human_mood_on_entry": np.random.choice(['Positive', 'Neutral', 'Negative'], size=20),
    "human_mood_on_exit": np.random.choice(['Positive', 'Neutral', 'Negative'], size=20),
    "human_mistake": ['Mistake ' + str(i) for i in range(1, 21)],
    "human_reflection_for_improvement": ['Improvement ' + str(i) for i in range(1, 21)],
}

df = pd.DataFrame(data)
df = df.sort_values(by="tradeinfo_entry_date", ascending=False)

# Write DataFrame to CSV
df.to_csv('trades.csv', index=False)
