journal_data_df_colums = [
    "tradeinfo_Ticker",
    "tradeinfo_entry_date",
    "tradeinfo_entry_price",
    "tradeinfo_exit_date",
    "tradeinfo_exit_price",
    "tradeinfo_number_shares",
    "tradeinfo_gain_percentage",
    "tradeinfo_gain_absolut",
    "tradeinfo_tax",
    "tradeinfo_fees",

    "fundamentals_sector",
    "fundamentals_market_cap",
    "fundamentals_price_to_earning",
    "fundamentals_price_to_book",
    "fundamentals_dept_to_equity",
    "fundamentals_free_cash_flow",
    "fundamentals_PEG_ratio",
    "fundamentals_market_sentiment",
    "fundamentals_additional_ideas",

    "technical_risk_reward_ratio",
    "technical_RSI",
    "technical_trend_mac_d",
    "technical_on_balance_volume",
    "technical_AD_line",
    "technical_ADX",
    "technical_aroon_indicator",

    "human_trading_idea_description",
    "human_mood_on_entry",
    "human_mood_on_exit",
    "human_mistake",
    "human_reflection_for_improvement",
    "human_picture_path",
]

sectors = [
    "Basic Materials",
    "Communication Services",
    "Consumer Cyclical",
    "Consumer Defensive",
    "Energy",
    "Financial Services",
    "Healthcare",
    "Industrials",
    "Technology",
    "Utilities",
    "Real Estate",
]

market_cap_ranges = [
    "300.000.000",
    "2.000.000.000",
    "10.000.000.000",
    "200.000.000.000",
    "1.000.000.000.000",
]

analyst_ratings = [
    "Strong Buy",
    "Buy",
    "Hold",
    "Sell",
    "Strong Sell"
]

risk_reward_ratios = ['1:1', '1:2', '1:3', '1:4', '1:5', '1:6', '1:7', '1:8']

market_sentiment = ["Bullish", "Sideways", "Bearish"]

sorted_moods = ["FOMO",
                "Euphoric",
                "Excited",
                "Confident",
                "Hopeful",
                "Satisfied",
                "Relieved",
                "Indifferent",
                "Unsure",
                "Anxious",
                "Regretful",
                "Disappointed",
                "Frustrated",
                "Fearful",
                "Greedy",
                "Desperate"]

trading_mistakes = [
    "No mistake made :)",
    "Trading without a plan",
    "Ignoring the overall market trend",
    "Buying based on recommendation without personal research",
    "Chasing a 'hot' tip or trend",
    "Buying high and selling low",
    "Neglecting risk management",
    "Overtrading",
    "Not setting a stop loss",
    "Not taking profits when the price reaches the target",
    "Letting emotions control decision-making",
    "Holding onto losing positions for too long",
    "Not diversifying portfolio",
    "Ignoring tax implications",
    "Trading with money one cannot afford to lose",
    "Not keeping a trading journal",
    "Neglecting to review and learn from past trades",
    "Failing to understand the company's business model",
    "Investing based on past performance alone",
    "Ignoring the financial health of the company",
    "Impulsive trading",
    "Ignoring important news and economic indicators",
    "Not understanding the products being traded",
    "Ignoring or misunderstanding key financial ratios",
    "Not researching the competitive landscape of the industry",
    "Misunderstanding market sentiment",
    "Over-reliance on technical analysis",
    "Ignoring or underestimating currency risk in international investments",
    "Failing to account for inflation and interest rates",
    "Underestimating the impact of political instability on markets",
    "Not considering the opportunity cost of investment decisions",
    "Investing without understanding the level of risk involved"
]
