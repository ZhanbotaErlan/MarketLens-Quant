# MarketLens-Quant

### Interactive Quantitative Market Analytics

A research-driven quantitative finance platform for exploring equity performance, financial risk, portfolio diversification, and systematic trading strategies.

**Tech Stack:** Python · Streamlit · Pandas · NumPy · Plotly · yfinance

---

## 1. Project Overview

**MarketLens** is an interactive quantitative market analytics platform developed as an extension of my independent research on U.S. technology and Kazakhstan-related equities.

The platform integrates historical financial data, quantitative risk measurement, portfolio analysis, and systematic strategy backtesting into a unified analytical environment.

My original research investigated differences in return behavior, volatility, correlation structures, diversification, and moving-average trend-following strategies across selected equities. MarketLens translates these methods into an interactive application, allowing users to modify financial instruments, observation periods, risk-free-rate assumptions, and strategy parameters.

The project's objective is not to predict future stock prices, but to make quantitative financial analysis more transparent, accessible, and reproducible.

---

## 2. Research Motivation

Financial markets differ in their return distributions, volatility, correlation patterns, and responses to systematic investment strategies.

My independent research, titled *Risk, Return, Diversification, and Trend-Following Strategies: Evidence from U.S. Technology and Kazakhstan-Related Equities*, examined these characteristics through historical data analysis.

Traditional research outputs, including academic papers and computational notebooks, often present results for predetermined datasets and assumptions. Readers cannot easily investigate how those results change when selecting different assets, modifying observation periods, or testing alternative trading rules.

MarketLens was developed to address this limitation.

By transforming quantitative research methods into an interactive application, the project seeks to:

1. **Improve analytical transparency** by presenting calculations, assumptions, and limitations clearly.
2. **Enable interactive exploration** of historical financial behavior under different assets and time periods.
3. **Support reproducible analysis** through a structured computational framework.

MarketLens represents a transition from static quantitative research toward a reusable analytical tool.

---

## 3. Core Analytical Modules

MarketLens consists of five analytical modules.

### 3.1 Market Overview — Single Asset Analytics

The Market Overview module evaluates the historical performance and risk characteristics of an individual equity.

**Key features:**

- Historical closing-price visualization
- Daily returns
- Cumulative returns
- Annualized arithmetic return
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Historical Value at Risk (VaR)
- Conditional Value at Risk (CVaR)
- 30-day rolling volatility
- MA20, MA50, MA100, and MA200
- Growth-of-$1 analysis
- Drawdown analysis

VaR and CVaR are calculated using historical daily returns and are intended for descriptive analysis rather than forward-looking risk prediction.

### 3.2 Comparison & Diversification

This module examines the relationships between multiple equities and their implications for portfolio diversification.

**Key features:**

- Multi-asset selection and comparison
- Matched-sample return analysis
- Pairwise correlation matrix
- 30-day rolling correlations
- Average pairwise correlation
- Equal-weighted portfolio construction
- Portfolio annualized return
- Portfolio annualized volatility
- Diversification ratio
- Cumulative portfolio wealth

Only overlapping trading dates are retained for multi-asset comparisons.

### 3.3 Strategy Lab

The Strategy Lab evaluates moving-average trend-following strategies against a Buy & Hold benchmark.

**Supported strategies:**

- MA20
- MA50
- MA100
- MA200

The strategy follows a long-or-cash framework. It holds the asset when its closing price is above the selected moving average and otherwise remains in cash.

To reduce look-ahead bias, the trading position is derived from the previous trading day's signal.

**Performance measures:**

- Cumulative return
- Annualized return
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Strategy wealth versus Buy & Hold
- Closing price versus moving average

The objective is to study the historical behavior and limitations of systematic trading rules rather than to identify a universally optimal strategy.

### 3.4 Costs & Robustness

The Costs & Robustness module examines how transaction costs and implementation assumptions affect strategy results.

The application uses three transaction-cost scenarios:

| Scenario | Assumed Cost |
|---|---:|
| Frictionless | 0 basis points |
| Low-cost scenario | 10 basis points |
| Higher-cost scenario | 25 basis points |

**Key features:**

- Position changes and trading turnover
- Transaction-cost-adjusted returns
- Cumulative strategy wealth under different cost assumptions
- Return reduction caused by transaction costs
- Annualized outperformance relative to Buy & Hold
- Strategy win rate
- Downside protection
- Robustness comparison tables

Transaction costs are applied whenever the strategy changes its position, including the initial entry into a position.

### 3.5 Methodology

The Methodology module documents the mathematical definitions and assumptions used throughout the application.

It explains:

- Return measurement
- Risk and volatility
- Sharpe ratio
- Drawdown
- Correlation and diversification
- Moving-average signals
- Trading positions
- Transaction costs
- Limitations of the backtesting framework

---

## 4. Quantitative Methodology

MarketLens applies established quantitative finance methods to historical daily equity data.

### 4.1 Daily Returns

Daily simple returns are calculated as:

$$
r_t=\frac{P_t}{P_{t-1}}-1
$$

where \(P_t\) represents the closing price at time \(t\).

### 4.2 Annualized Arithmetic Return

Annualized arithmetic return is defined as:

$$
R_{annual}=252\times\overline{r}
$$

where \(\overline{r}\) is the average daily return.

This is an annualized arithmetic return, not a compound annual growth rate.

### 4.3 Annualized Volatility

Annualized volatility is calculated as:

$$
\sigma_{annual}=\sigma_{daily}\sqrt{252}
$$

The calculation assumes 252 trading days per year.

### 4.4 Sharpe Ratio

The Sharpe ratio is calculated as:

$$
SR=\frac{\overline{r-r_f}}{\sigma(r-r_f)}\sqrt{252}
$$

The annual risk-free rate is converted into an equivalent daily rate before calculation.

The application uses a user-configurable annual risk-free rate. The default value is 4.97%.

### 4.5 Maximum Drawdown

Drawdown measures the decline in cumulative wealth relative to its previous peak:

$$
D_t=\frac{W_t}{\max_{s\leq t}W_s}-1
$$

Maximum drawdown is defined as:

$$
MDD=\min_t(D_t)
$$

### 4.6 Portfolio Diversification

For an equal-weighted portfolio containing \(N\) assets:

$$
w_i=\frac{1}{N}
$$

The diversification ratio is:

$$
DR=\frac{\sum_{i=1}^{N}w_i\sigma_i}{\sigma_p}
$$

where \(\sigma_i\) is the annualized volatility of asset \(i\), and \(\sigma_p\) is the annualized portfolio volatility.

### 4.7 Moving-Average Trend Following

The strategy generates a signal according to the relationship between the closing price and its moving average:

$$
Signal_t=
\begin{cases}
1,&P_t>MA_t\\
0,&P_t\leq MA_t
\end{cases}
$$

The trading position is lagged by one day:

$$
Position_t=Signal_{t-1}
$$

The daily strategy return is calculated as:

$$
r_{strategy,t}=Position_t\times r_t
$$

### 4.8 Transaction-Cost Adjustment

Position changes are measured as:

$$
Turnover_t=|Position_t-Position_{t-1}|
$$

Net strategy return is defined as:

$$
r_{net,t}=r_{gross,t}-Turnover_t\times c
$$

where \(c\) represents the assumed one-way transaction cost.

---

## 5. Research Design & Assumptions

### Matched Trading Dates

Multi-asset analyses align observations to overlapping trading dates. This allows correlations and portfolio metrics to be evaluated over a common sample.

### Historical Data

The platform retrieves historical equity market data from Yahoo Finance through `yfinance`.

Reported metrics are descriptive and should not be interpreted as predictions of future market performance. Results may change when the data source is updated or when different dates and instruments are selected.

### Lagged Trading Signals

Moving-average strategies use one-day-lagged trading positions to reduce look-ahead bias.

### Simplified Backtesting Framework

The strategy evaluation assumes a long-or-cash position and calculates close-to-close returns. It does not simulate every aspect of real-world order execution.

The framework does not fully model:

- Bid-ask spreads
- Slippage
- Market impact
- Liquidity constraints
- Taxes
- Portfolio rebalancing costs
- Different execution prices

### Transaction-Cost Sensitivity

Multiple transaction-cost scenarios are used to investigate whether strategy performance remains attractive under alternative implementation assumptions.

### Research Scope

The underlying research focuses on selected U.S. technology and Kazakhstan-related equities. These securities should not be interpreted as comprehensive representations of either national stock market.

---

## 6. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Quantitative computation and application logic |
| Streamlit | Interactive web application |
| Pandas | Financial time-series manipulation and analysis |
| NumPy | Numerical and statistical computation |
| Plotly | Interactive financial data visualization |
| yfinance | Historical equity data retrieval |

---

## 7. Getting Started

### Prerequisites

- Python
- Internet connection for historical market data retrieval

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/ZhanbotaErlan/MarketLens-Quant.git
cd MarketLens-Quant
```

#### 2. Create a virtual environment

```bash
python -m venv .venv
```

#### 3. Activate the virtual environment

For macOS/Linux:

```bash
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

#### 4. Install dependencies

```bash
pip install -r requirement.txt
```

#### 5. Run the application

```bash
streamlit run app.py
```

The application will normally open at:

```text
http://localhost:8501
```

---

## 8. Connection to Independent Research

MarketLens was developed as an extension of the independent research project:

**Risk, Return, Diversification, and Trend-Following Strategies: Evidence from U.S. Technology and Kazakhstan-Related Equities**

The original research investigated historical market behavior through:

- Return and volatility analysis
- Correlation analysis
- Risk-adjusted performance evaluation
- Portfolio diversification
- Moving-average trend-following strategies
- Transaction-cost sensitivity analysis

MarketLens extends this analytical framework by making the underlying methods interactive and reusable.

Rather than limiting analysis to predetermined combinations of assets and parameters, the application enables users to investigate how quantitative results change under different assumptions.

**Original Research Repository:**

https://github.com/ZhanbotaErlan/US-Kazakhstan-Stock-Analysis

---

## 9. Limitations & Disclaimer

MarketLens is intended for educational and research purposes.

The application relies on historical financial data, which may be incomplete, revised, or affected by differences in market conventions.

The strategy backtests use simplified assumptions and do not fully incorporate real-world execution conditions such as:

- Bid-ask spreads
- Slippage
- Market impact
- Liquidity constraints
- Taxes
- Portfolio rebalancing costs
- Different execution prices

Historical results do not guarantee future performance.

MarketLens does not provide investment advice, investment recommendations, or guarantees of financial returns.

---

*MarketLens — From quantitative research to interactive financial analytics.*
