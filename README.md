## Overview
The Trading Journal App is an open-source initiative aimed at helping traders maintain a disciplined, systematic, and reflective approach to their trading activities. This application is designed with user-friendly interfaces and is easy to install and navigate, making it ideal even for non-coders.

## Goal of the Application
The primary goal of the Trading Journal App is to assist traders in tracking their trading activities, evaluating performance metrics, and making informed trading decisions based on analytical insights. The application promotes discipline by enabling traders to maintain a comprehensive record of their trades and offers a platform for continuous self-improvement and reflection.

## Data which is beeing tracked, analized and locally stored

Basic trade info:
* tradeinfo_Ticker
* tradeinfo_entry_date
* tradeinfo_entry_price
* tradeinfo_exit_date
* tradeinfo_exit_price
* tradeinfo_gain_percentage
* tradeinfo_gain_absolut
* tradeinfo_tax
* tradeinfo_fees
* tradeinfo_exchange

fundamental analysis:
* fundamentals_sector
* fundamentals_market_cap
* fundamentals_price_to_earning
* fundamentals_price_to_book
* fundamentals_dept_to_equity
* fundamentals_free_cash_flow
* fundamentals_PEG_ratio
* fundamentals_general_market_analysis
* fundamentals_additional_ideas

technical analysis:
* technical_RSI
* technical_trend_mac_d
* technical_on_balance_volume
* technical_AD_line
* technical_ADX
* technical_aroon_indicator

human stats:
* human_trading_idea_description
* human_mood_on_entry
* human_mood_on_exit
* human_mistake
* human_reflection_for_improvement

## Features
Dashboard: The dashboard provides a snapshot of various performance metrics and statistics which includes:

* Total number of trades
* Number of winning and losing trades
* Win rate
* Average win and loss
* Profit factor
* Drawdown
* Risk-reward ratio
* Average risk-reward ratio
* Expectancy

#### Trade List: This feature allows users to view all their trades, input new trades, and make detailed notes on each trade. Users can also annotate screenshots from chart software for easy visual reference.

#### Analysis: The Analysis section aids in understanding individual mistakes and learning from them. It displays a plethora of stats for better trade optimization:

* Performance metrics per symbol
* Most and least profitable symbols
* Symbols with the highest win rate
* Symbols with the most trades 

## Contributions
Open-source developers are heartily welcomed to contribute to this project. If you're a developer looking to contribute to a project with real-world utility, this is the perfect opportunity. Your contributions can help shape this app and make a significant difference in the lives of traders around the world.

Your contributions can take many forms: from improvements in the codebase, adding new features, improving the user interface, to optimizing the current implementations. Please feel free to explore the issues and pull requests to see where you can lend your skills.


## Installation

Together, let's build a better, smarter, and more efficient trading environment for everyone. Join us on this exciting journey!

## Improvements planned

* dont show classification in dataframe columns (not possible)
* add technical analysis picture to trade ()
* add back and restore function
* add Installation description also with Docker
* add tax and fee in %
* make comparison chart capable with different y-axis 
* memorize chart settings like 
* Grouping manage trades more space efficient
* Refactor code, split into modules