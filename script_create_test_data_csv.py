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
    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='s')


start = pd.to_datetime('2021-01-01')
end = pd.to_datetime('2023-12-31')

data = {
    "tradeinfo_Ticker": np.random.choice(['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'], size=20),
    "tradeinfo_entry_date": random_dates(start, end, 20),
    "tradeinfo_entry_price": np.random.uniform(100, 500, size=20),
    "tradeinfo_number_shares": np.random.randint(1, 50, size=20),
    "tradeinfo_exit_date": random_dates(start, end, 20),
    "tradeinfo_exit_price": np.random.uniform(100, 500, size=20),
    "tradeinfo_gain_percentage": np.random.uniform(-0.2, 0.2, size=20),
    "tradeinfo_gain_absolut": np.random.uniform(-100, 100, size=20),
    "tradeinfo_tax": np.random.uniform(10, 30, size=20),
    "tradeinfo_fees": np.random.uniform(1, 10, size=20),

    "fundamentals_sector": np.random.choice(
        data_specs.sectors, size=20),
    "fundamentals_market_cap": np.random.choice(data_specs.market_cap_ranges, size=20),
    "fundamentals_price_to_earning": np.random.uniform(10, 30, size=20),
    "fundamentals_price_to_book": np.random.uniform(1, 10, size=20),
    "fundamentals_dept_to_equity": np.random.uniform(0.1, 2, size=20),
    "fundamentals_free_cash_flow": np.random.uniform(10 ** 6, 10 ** 9, size=20),
    "fundamentals_PEG_ratio": np.random.uniform(0.5, 2, size=20),
    "fundamentals_market_sentiment": np.random.choice(data_specs.market_sentiment, size=20),
    "fundamentals_analyst_rating": np.random.choice(data_specs.analyst_ratings, size=20),

    "technical_risk_reward_ratio": np.random.choice(data_specs.risk_reward_ratios, size=20),
    "technical_RSI": np.random.uniform(0, 100, size=20),
    "technical_trend_mac_d": np.random.uniform(-5, 5, size=20),
    "technical_on_balance_volume": np.random.uniform(10 ** 6, 10 ** 9, size=20),
    "technical_AD_line": np.random.uniform(0, 1, size=20),
    "technical_ADX": np.random.uniform(0, 100, size=20),
    "technical_aroon_indicator": np.random.uniform(0, 100, size=20),

    "human_trading_idea_description": ['Idea ' + str(i) for i in range(1, 21)],
    "human_mood_on_entry": np.random.choice(data_specs.sorted_moods, size=20),
    "human_mood_on_exit": np.random.choice(data_specs.sorted_moods, size=20),
    "human_mistake": np.random.choice(data_specs.trading_mistakes, size=20),
    "human_reflection_for_improvement": ['Improvement ' + str(i) for i in range(1, 21)],

    "human_picture_path": "Here Is A Default Path",

}

df = pd.DataFrame(data)
df = df.sort_values(by="tradeinfo_entry_date", ascending=False)

# Write DataFrame to CSV
df.to_csv('trades.csv', index=False)
