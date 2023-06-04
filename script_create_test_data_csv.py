from pathlib import Path
import sys
import pandas as pd
import numpy as np
import data_specs

np.random.seed(42)  # for reproducibility

# Function to generate random dates
def random_dates(start, end, n=10):
    start_u = start.value // 10 ** 9
    end_u = end.value // 10 ** 9
    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='s').date


start = pd.to_datetime('2021-01-01')
end = pd.to_datetime('2023-12-31')

num_rows = 10  # Set this to the number of rows you want

data = {
    "tradeinfo_Ticker": np.random.choice(['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'], size=num_rows),
    "tradeinfo_entry_date": random_dates(start, end, num_rows),
    "tradeinfo_entry_price": np.random.uniform(100, 500, size=num_rows),
    "tradeinfo_number_shares": np.random.randint(1, 50, size=num_rows),
    "tradeinfo_exit_date": random_dates(start, end, num_rows),
    "tradeinfo_exit_price": np.random.uniform(100, 500, size=num_rows),
    "tradeinfo_gain_percentage": np.random.uniform(-0.2, 0.2, size=num_rows),
    "tradeinfo_gain_absolut": np.random.uniform(-100, 100, size=num_rows),
    "tradeinfo_tax": np.random.uniform(10, 30, size=num_rows),
    "tradeinfo_fees": np.random.uniform(1, 10, size=num_rows),

    "fundamentals_sector": np.random.choice(data_specs.sectors, size=num_rows),
    "fundamentals_market_cap": np.random.choice(data_specs.market_cap_ranges, size=num_rows),
    "fundamentals_price_to_earning": np.random.uniform(10, 30, size=num_rows),
    "fundamentals_price_to_book": np.random.uniform(1, 10, size=num_rows),
    "fundamentals_dept_to_equity": np.random.uniform(0.1, 2, size=num_rows),
    "fundamentals_free_cash_flow": np.random.uniform(10 ** 6, 10 ** 9, size=num_rows),
    "fundamentals_PEG_ratio": np.random.uniform(0.5, 2, size=num_rows),
    "fundamentals_market_sentiment": np.random.choice(data_specs.market_sentiment, size=num_rows),
    "fundamentals_analyst_rating": np.random.choice(data_specs.analyst_ratings, size=num_rows),

    "technical_risk_reward_ratio": np.random.choice(data_specs.risk_reward_ratios, size=num_rows),
    "technical_RSI": np.random.uniform(0, 100, size=num_rows),
    "technical_trend_mac_d": np.random.uniform(-5, 5, size=num_rows),
    "technical_on_balance_volume": np.random.uniform(10 ** 6, 10 ** 9, size=num_rows),
    "technical_AD_line": np.random.uniform(0, 1, size=num_rows),
    "technical_ADX": np.random.uniform(0, 100, size=num_rows),
    "technical_aroon_indicator": np.random.uniform(0, 100, size=num_rows),

    "human_trading_idea_description": ['Idea ' + str(i) for i in range(1, num_rows+1)],
    "human_mood_on_entry": np.random.choice(data_specs.sorted_moods, size=num_rows),
    "human_mood_on_exit": np.random.choice(data_specs.sorted_moods, size=num_rows),
    "human_mistake": np.random.choice(data_specs.trading_mistakes, size=num_rows),
    "human_reflection_for_improvement": ['Improvement ' + str(i) for i in range(1, num_rows+1)],
    "human_picture_path": "Here Is A Default Path",
}


df = pd.DataFrame(data)
df = df.sort_values(by="tradeinfo_entry_date", ascending=False)

# Write DataFrame to CSV
df.to_csv('trades.csv', index=False)
