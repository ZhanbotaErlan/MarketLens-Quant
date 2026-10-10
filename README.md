# MarketLens-Quant
### Interactive Quantitative Market Analytics

**A research-driven quantitative finance platform for exploring equity performance, financial risk, portfolio diversification, and systematic trading strategies.**

**Tech Stack:** Python · Streamlit · Pandas · NumPy · Plotly · yfinance

---

## 1. Project Overview

**MarketLens** is an interactive quantitative market analytics platform developed as an extension of independent research on U.S. technology and Kazakhstan-related equities.

The platform integrates historical financial data, quantitative risk measurement, portfolio analysis, and systematic strategy backtesting into a unified analytical environment.

My original research investigated differences in return behavior, volatility, correlation structures, and the performance of moving-average trend-following strategies across selected equities. MarketLens translates these methods into an interactive application, allowing users to modify financial instruments, observation periods, and strategy parameters.

The project's objective is not to predict future stock prices, but to make quantitative financial analysis more transparent, accessible, and reproducible.

## 2. Research Motivation

Financial markets differ in their return distributions, volatility, correlation patterns, and responses to systematic investment strategies.

My independent research, titled *Risk, Return Analysis and Trend-Following Strategies: Evidence from U.S. Technology and Kazakhstan-Related Equities*, examined these characteristics through historical data analysis.

However, traditional research outputs, including academic papers and computational notebooks, often present results for predetermined datasets and assumptions. Readers cannot easily investigate how those results change when selecting different assets, modifying observation periods, or testing alternative trading rules.

MarketLens was developed to address this limitation.

By transforming quantitative research methods into an interactive application, the project seeks to achieve three objectives:

1. **Analytical Transparency:** Make quantitative calculations, underlying assumptions, and model limitations understandable.
2. **Interactive Exploration:** Enable users to examine historical financial behavior under different assets, time periods, and analytical parameters.
3. **Research Reproducibility:** Provide a structured computational framework through which financial metrics and strategy results can be reproduced and inspected.

MarketLens represents a transition from static quantitative research toward a reusable analytical tool.

## 3. Core Analytical Modules

MarketLens consists of five interconnected analytical modules.

### 3.1 Market Overview — Single Asset Analytics

The Market Overview module provides a comprehensive evaluation of individual equity performance and financial risk.

**Key Features:**

- Historical closing-price visualization
- Daily and cumulative returns
- Annualized arithmetic return
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Historical Value at Risk (VaR)
- Conditional Value at Risk (CVaR)
- 30-day rolling volatility
- Moving averages: MA20, MA50, MA100, and MA200
- Growth-of-$1 and drawdown analysis

Together, these indicators allow users to evaluate both historical return characteristics and downside risk.

### 3.2 Comparison & Diversification

This module examines the relationships between multiple equities and their implications for portfolio diversification.

**Key Features:**

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

By combining correlation measures with portfolio-level statistics, the module enables users to investigate how asset relationships influence overall portfolio risk.

### 3.3 Strategy Lab

The Strategy Lab evaluates moving-average trend-following strategies against a Buy & Hold benchmark.

**Supported Strategies:**

- MA20
- MA50
- MA100
- MA200

The strategy operates within a long-or-cash framework, generating exposure based on whether the closing price is above or below its selected moving average.

To reduce look-ahead bias, the trading position is derived from the previous trading day's signal.

**Performance Evaluation:**

- Cumulative return
- Annualized return
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Strategy wealth versus Buy & Hold
- Closing price versus moving average

The objective is to study the historical behavior, benefits, and limitations of systematic trading rules rather than to identify a universally optimal strategy.

### 3.4 Costs & Robustness

Historical backtesting results may be sensitive to transaction costs and strategy implementation assumptions.

The Costs & Robustness module investigates these effects under three transaction-cost scenarios.

| Scenario | Assumed Cost |
|---|---|
| Frictionless | 0 basis points |
| Low-cost scenario | 10 basis points |
| Higher-cost scenario | 25 basis points |

**Key Features:**

- Position changes and trading turnover
- Transaction-cost-adjusted returns
- Cumulative strategy wealth across cost assumptions
- Return reduction caused by transaction costs
- Annualized outperformance relative to Buy & Hold
- Strategy win rate
- Downside protection
- Robustness comparison tables

This module highlights the importance of evaluating systematic strategies beyond frictionless backtesting assumptions.

### 3.5 Methodology

The Methodology module documents the mathematical definitions and assumptions underlying MarketLens.

It explains the calculations associated with:

- Return measurement
- Risk and volatility
- Sharpe ratio
- Drawdown
- Correlation and diversification
- Moving-average signals
- Trading positions
- Transaction costs

The emphasis on methodological transparency allows users to understand how analytical results are produced.

---

## 4. Quantitative Methodology

MarketLens applies established quantitative finance methods to historical daily equity data.

### 4.1 Daily Returns

Daily simple returns are calculated as:

$$
r_t=\frac{P_t}{P_{t-1}}-1
$$

where \(P_t\) represents the closing price at time \(t\).

### 4.2 Annualized Return

Annualized arithmetic return is defined as:

$$
R_{annual}=252\times\overline{r}
$$

where \(\overline{r}\) is the average daily return.

### 4.3 Annualized Volatility

Annualized volatility is calculated as:

$$
\sigma_{annual}=\sigma_{daily}\sqrt{252}
$$

The calculation assumes 252 trading days per year.

### 4.4 Sharpe Ratio

The Sharpe ratio evaluates risk-adjusted performance:

$$
SR=\frac{\overline{r-r_f}}{\sigma(r-r_f)}\sqrt{252}
$$

The annual risk-free rate is converted into an equivalent daily rate before calculation.

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

The strategy generates a signal according to the relationship between closing prices and moving averages:

$$
Signal_t=
\begin{cases}
1,&P_t>MA_t\\
0,&P_t\leq MA_t
\end{cases}
$$

To avoid directly using information from the current trading day's closing price to determine the same day's exposure, the trading position is lagged:

$$
Position_t=Signal_{t-1}
$$

Daily strategy return is calculated as:

$$
r_{strategy,t}=Position_t\times r_t
$$

### 4.8 Transaction-Cost Adjustment

Transaction costs are applied whenever the strategy changes its position:

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

MarketLens is designed around methodological clarity and consistent quantitative evaluation.

**Matched Trading Dates**

Multi-asset analyses align observations to overlapping trading dates, allowing correlations and portfolio metrics to be evaluated over a common sample.

**Historical Data**

The platform uses historical equity market data. Reported metrics are descriptive and should not be interpreted as predictions of future market performance.

**Lagged Trading Signals**

Moving-average strategies use one-day-lagged trading positions to reduce look-ahead bias.

**Simplified Backtesting Framework**

The strategy evaluation assumes a long-or-cash position and calculates close-to-close returns. It does not simulate all aspects of real-world order execution.

**Transaction-Cost Sensitivity**

Multiple transaction-cost scenarios are used to investigate whether strategy performance remains attractive under alternative implementation assumptions.

**Research Scope**

The underlying research focuses on selected U.S. technology and Kazakhstan-related equities. These assets should not be interpreted as comprehensive representations of either national stock market.

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

- Python installed locally
- Internet connection for market data retrieval

### Installation

**1. Clone the repository**

```bash
git clone [https://github.com/ZhanbotaErlan/MarketLens-Quant.git]
cd MarketLens-Quant
```

**2. Create a virtual environment**

```bash
python3 -m venv .venv
```

**3. Activate the environment**

For macOS/Linux:

```bash
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Run the application**

```bash
streamlit run app.py
```

The application will normally open at:

`http://localhost:8501`

---

## 8. Project Screenshots

### Market Overview

*Screenshot to be added: Historical price performance, financial metrics, and risk analysis.*

### Comparison & Diversification

*Screenshot to be added: Correlation matrix, rolling correlations, and portfolio diversification metrics.*

### Strategy Lab

*Screenshot to be added: Moving-average strategy results and Buy & Hold comparison.*

### Costs & Robustness

*Screenshot to be added: Transaction-cost sensitivity and strategy robustness evaluation.*

---

## 9. Connection to Independent Research

MarketLens was developed as an extension of the independent research project:

**Risk, Return Analysis and Trend-Following Strategies: Evidence from U.S. Technology and Kazakhstan-Related Equities**

The original research investigated historical market behavior through:

- Return and volatility analysis
- Correlation analysis
- Risk-adjusted performance evaluation
- Portfolio diversification
- Moving-average trend-following strategies

MarketLens extends this analytical framework by making the underlying methods interactive and reusable.

Rather than limiting analysis to predetermined combinations of assets and parameters, the application enables users to conduct additional investigations and examine how quantitative outcomes change under different assumptions.

**Original Research Repository:** [https://github.com/ZhanbotaErlan/US-Kazakhstan-Stock-Analysis.git]

---

## 10. Limitations & Disclaimer

MarketLens is intended for educational and research purposes.

The application relies on historical financial data, which may be incomplete, revised, or affected by differences in market conventions.

Strategy backtests use simplified assumptions and do not fully incorporate real-world execution conditions such as slippage, market impact, liquidity constraints, taxes, or other implementation costs.

Historical results do not guarantee future performance.

**MarketLens does not provide investment advice, investment recommendations, or guarantees of financial returns.**

---

*MarketLens — From quantitative research to interactive financial analytics.*
