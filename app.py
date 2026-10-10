import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MarketLens",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

TRADING_DAYS = 252
DEFAULT_RF = 0.0497


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- APP BACKGROUND ---------- */

    .stApp {
        background: #f5f7fb;
        color: #1f2430;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }


    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e7eaf0;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }


    /* ---------- TEXT ---------- */

    h1, h2, h3 {
        color: #1e2430;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    p {
        color: #6c7480;
    }


    /* ---------- CARDS ---------- */

    .ml-card {
        background: #ffffff;
        border: 1px solid #e9edf3;
        border-radius: 18px;
        padding: 20px 22px;
        box-shadow: 0 2px 8px rgba(28, 39, 60, 0.04);
        height: 100%;
    }

    .ml-card-title {
        font-size: 13px;
        font-weight: 600;
        color: #939aa5;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .ml-card-value {
        font-size: 28px;
        font-weight: 700;
        color: #202633;
        margin-bottom: 4px;
    }

    .ml-card-caption {
        font-size: 12px;
        color: #a4aab3;
    }


    /* ---------- METRICS ---------- */

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e9edf3;
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(28, 39, 60, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #8e96a3;
        font-size: 13px;
    }

    div[data-testid="stMetricValue"] {
        color: #202633;
        font-weight: 700;
        font-size: 28px;
    }


    /* ---------- BUTTON ---------- */

    .stButton > button {
        border-radius: 12px;
        height: 44px;
        font-weight: 600;
        border: none;
        background: linear-gradient(90deg, #7c6df2, #9a8df6);
        color: white;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #7162ec, #8c7ff1);
        color: white;
    }


    /* ---------- INPUTS ---------- */

    input {
        border-radius: 10px !important;
    }

    div[data-baseweb="input"] {
        border-radius: 10px !important;
    }


    /* ---------- PLOTLY ---------- */

    div[data-testid="stPlotlyChart"] {
        background: #ffffff;
        border: 1px solid #e9edf3;
        border-radius: 18px;
        padding: 8px;
        box-shadow: 0 2px 8px rgba(28, 39, 60, 0.04);
    }


    /* ---------- HIDE DEFAULT MENU ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATA FUNCTIONS
# =========================================================

@st.cache_data
def load_data(ticker, start_date, end_date):

    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False
    )

    if data.empty:
        return None

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data


def calculate_metrics(close, annual_rf):

    returns = close.pct_change().dropna()

    cumulative_return = (1 + returns).prod() - 1

    annual_return = returns.mean() * TRADING_DAYS

    annual_volatility = (
        returns.std() * np.sqrt(TRADING_DAYS)
    )

    daily_rf = (
        (1 + annual_rf) ** (1 / TRADING_DAYS)
    ) - 1

    excess_returns = returns - daily_rf

    if excess_returns.std() != 0:
        sharpe_ratio = (
            excess_returns.mean()
            / excess_returns.std()
            * np.sqrt(TRADING_DAYS)
        )
    else:
        sharpe_ratio = np.nan

    wealth = (1 + returns).cumprod()

    peak = wealth.cummax()

    drawdown = wealth / peak - 1

    max_drawdown = drawdown.min()

    var_95 = returns.quantile(0.05)

    cvar_95 = returns[
        returns <= var_95
    ].mean()

    rolling_vol = (
        returns.rolling(30).std()
        * np.sqrt(TRADING_DAYS)
    )

    return {
        "returns": returns,
        "cumulative_return": cumulative_return,
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe_ratio": sharpe_ratio,
        "wealth": wealth,
        "drawdown": drawdown,
        "max_drawdown": max_drawdown,
        "var_95": var_95,
        "cvar_95": cvar_95,
        "rolling_vol": rolling_vol
    }

# =========================================================
# CHART STYLE
# =========================================================

def apply_chart_style(fig, height=340, showlegend=True):

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        hovermode="x unified",

        font=dict(
            color="#5f6672",
            size=12
        ),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor="#edf0f4",
            tickfont=dict(color="#8a919d")
        ),

        yaxis=dict(
            gridcolor="#eef1f5",
            zeroline=False,
            linecolor="#edf0f4",
            tickfont=dict(color="#8a919d")
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        showlegend=showlegend
    )

    return fig    


# =========================================================
# SIDEBAR / CONTROL CENTER
# =========================================================
st.markdown(
    """
    <style>

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #edf0f5;
    }

    /* Sidebar inner spacing */
    section[data-testid="stSidebar"] > div {
        padding-top: 1.6rem;
    }

    /* Navigation radio items */
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent;
        border-radius: 10px;
        padding: 8px 10px;
        margin-bottom: 3px;
        transition: all 0.15s ease;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: #f5f3ff;
    }

    /* Input boxes */
    section[data-testid="stSidebar"] input {
        border-radius: 10px !important;
    }

    /* Analyze button */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border: none;
        border-radius: 11px;
        padding: 0.65rem 1rem;
        font-weight: 700;
        color: white;
        background: linear-gradient(
            90deg,
            #7c6df2 0%,
            #9b8df7 100%
        );
        box-shadow: 0 6px 18px rgba(124, 109, 242, 0.20);
        transition: all 0.18s ease;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 22px rgba(124, 109, 242, 0.28);
    }

    /* Divider */
    section[data-testid="stSidebar"] hr {
        margin-top: 18px;
        margin-bottom: 18px;
        border-color: #eef1f5;
    }

    /* Labels */
    section[data-testid="stSidebar"] label {
        color: #555e6d;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.sidebar.markdown(
    """
    <div style="
        font-size: 26px;
        font-weight: 800;
        color: #202633;
        margin-bottom: 2px;
    ">
        MarketLens
    </div>

    <div style="
        font-size: 12px;
        color: #969daa;
        margin-bottom: 22px;
    ">
        Quantitative Market Analytics
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------

st.sidebar.markdown("### Navigation")

section = st.sidebar.radio(
    "Navigation",
    [
        "Overview / Single Asset",
        "Comparison & Diversification",
        "Strategy Lab",
        "Costs & Robustness",
        "Methodology"
    ],
    label_visibility="collapsed"
)


st.sidebar.markdown("---")


# ---------------------------------------------------------
# ANALYSIS SETTINGS
# ---------------------------------------------------------

st.sidebar.markdown("### Analysis Settings")

ticker = st.sidebar.text_input(
    "Ticker",
    value="AAPL"
).upper().strip()


start_date = st.sidebar.date_input(
    "Start Date",
    value=date(2020, 1, 1),
    min_value=date(1970, 1, 1),
    max_value=date.today()
)


end_date = st.sidebar.date_input(
    "End Date",
    value=date.today(),
    min_value=date(1970, 1, 1),
    max_value=date.today()
)


annual_rf = st.sidebar.number_input(
    "Risk-Free Rate",
    min_value=0.0,
    max_value=0.20,
    value=DEFAULT_RF,
    step=0.001,
    format="%.4f"
)


# ---------------------------------------------------------
# ANALYZE STATE
# ---------------------------------------------------------

if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False


if st.sidebar.button(
    "Analyze",
    use_container_width=True
):
    st.session_state.analysis_ready = True


analyze = st.session_state.analysis_ready


st.sidebar.markdown("---")

st.sidebar.caption(
    "Historical market data · Quantitative research tools"
)


# =====================================================
# DYNAMIC HEADER
# =====================================================

page_headers = {
    "Overview / Single Asset": {
        "title": "Market Overview",
        "subtitle": (
            "Explore historical performance, risk and market behavior "
            "using transparent quantitative metrics."
        ),
    },

    "Comparison & Diversification": {
        "title": "Comparison & Diversification",
        "subtitle": (
            "Compare assets using matched samples, correlation, "
            "portfolio risk and diversification metrics."
        ),
    },

    "Strategy Lab": {
        "title": "Strategy Lab",
        "subtitle": (
            "Backtest moving-average trend-following strategies "
            "against a Buy & Hold benchmark."
        ),
    },

    "Costs & Robustness": {
        "title": "Costs & Robustness",
        "subtitle": (
            "Evaluate transaction costs, turnover, downside protection "
            "and strategy robustness."
        ),
    },

    "Methodology": {
        "title": "Methodology",
        "subtitle": (
            "Review the formulas, assumptions and quantitative methods "
            "used throughout MarketLens."
        ),
    },
}

current_header = page_headers[section]

top1, top2 = st.columns([4, 1])

with top1:

    st.markdown(
        """
        <div style="
            font-size: 14px;
            font-weight: 600;
            color: #9a8df6;
            margin-bottom: 8px;
        ">
            QUANTITATIVE MARKET ANALYTICS
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="
            font-size: 38px;
            font-weight: 800;
            color: #202633;
            margin-bottom: 4px;
        ">
            {current_header["title"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="
            font-size: 16px;
            color: #7c8490;
            margin-bottom: 24px;
        ">
            {current_header["subtitle"]}
        </div>
        """,
        unsafe_allow_html=True
    )

with top2:

    st.markdown(
        """
        <div style="
            background: #ffffff;
            border: 1px solid #e9edf3;
            border-radius: 14px;
            padding: 12px 16px;
            text-align: center;
            color: #7b8290;
            margin-top: 12px;
        ">
            MarketLens
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# ANALYSIS
# =========================================================


# =========================================================
# ANALYSIS GATE
# =========================================================

if not analyze:
    st.html(
        """
        <div style="
            background: #ffffff;
            border: 1px solid #e9edf3;
            border-radius: 20px;
            padding: 48px 42px;
            margin-top: 20px;
        ">
            <div style="
                font-size: 13px;
                font-weight: 700;
                color: #8b7cf6;
                margin-bottom: 12px;
            ">
                MARKETLENS
            </div>

            <div style="
                font-size: 30px;
                font-weight: 800;
                color: #202633;
                margin-bottom: 12px;
            ">
                Quantitative Market Analytics
            </div>

            <div style="
                font-size: 16px;
                color: #7c8490;
                line-height: 1.7;
                max-width: 680px;
            ">
                Select a section from the navigation menu,
                configure your analysis settings, and click
                <b>Analyze</b> to begin exploring market performance,
                risk, diversification and trading strategies.
            </div>
        </div>
        """
    )

    st.stop()
if section == "Overview / Single Asset":   
    if analyze:

        if not ticker:
            st.error("Please enter a ticker symbol.")
            st.stop()

        if start_date >= end_date:
            st.error("The start date must be earlier than the end date.")
            st.stop()

        with st.spinner(f"Loading market data for {ticker}..."):
            data = load_data(ticker, start_date, end_date)

        if data is None:
            st.error("No market data were found.")
            st.stop()

        close = data["Close"].dropna()

        if len(close) < 30:
            st.error("Not enough observations were found.")
            st.stop()

        metrics = calculate_metrics(close, annual_rf)

        technical_data = pd.DataFrame({"Close": close})
        technical_data["MA20"] = technical_data["Close"].rolling(20).mean()
        technical_data["MA50"] = technical_data["Close"].rolling(50).mean()
        technical_data["MA100"] = technical_data["Close"].rolling(100).mean()
        technical_data["MA200"] = technical_data["Close"].rolling(200).mean()

        # ASSET HEADER
        st.markdown(
            """
            <style>

            /* KPI cards */
            div[data-testid="stMetric"] {
                background: #ffffff;
                border: 1px solid #e9edf3;
                border-radius: 16px;
                padding: 18px 20px;
                box-shadow: 0 4px 14px rgba(32, 38, 51, 0.04);
            }

            /* KPI label */
            div[data-testid="stMetric"] label {
                color: #8a919d !important;
                font-size: 13px !important;
                font-weight: 600 !important;
            }

            /* KPI value */
            div[data-testid="stMetric"] [data-testid="stMetricValue"] {
                color: #202633;
                font-size: 26px;
                font-weight: 750;
            }

            /* KPI delta */
            div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
                font-size: 13px;
            }

            </style>
            """,
            unsafe_allow_html=True
        )

        # KPI CARDS
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Return", f"{metrics['cumulative_return']:.2%}")
        c2.metric("Annualized Return", f"{metrics['annual_return']:.2%}")
        c3.metric("Annualized Volatility", f"{metrics['annual_volatility']:.2%}")
        c4.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.3f}")

        st.write("")

        # TOP ROW
        left, right = st.columns([2.1, 1])
        
        with left:

            st.markdown("#### Market Performance")

            price_fig = go.Figure()

            price_fig.add_trace(
                go.Scatter(
                    x=technical_data.index,
                    y=technical_data["Close"],
                    mode="lines",
                    name="Close",
                    line=dict(
                        width=2.4,
                        color="#8375ef"
                    )
                )
            )

            price_fig.update_layout(
                height=360,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                hovermode="x unified",
                font=dict(
                    color="#5f6672",
                    size=12
                ),
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    linecolor="#edf0f4",
                    tickfont=dict(color="#8a919d")
                ),
                yaxis=dict(
                    gridcolor="#eef1f5",
                    zeroline=False,
                    linecolor="#edf0f4",
                    tickfont=dict(color="#8a919d")
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                showlegend=False
            )

            st.plotly_chart(
                price_fig,
                use_container_width=True
            )


        with right:
            st.markdown("#### Risk Overview")
            st.metric("Maximum Drawdown", f"{metrics['max_drawdown']:.2%}")
            st.metric("95% Daily VaR", f"{metrics['var_95']:.2%}")
            st.metric("95% Daily CVaR", f"{metrics['cvar_95']:.2%}")

        # TREND SIGNALS
        st.write("")
        st.markdown(
            """
            <div style="
                font-size: 18px;
                font-weight: 700;
                color: #202633;
                margin-bottom: 12px;
            ">
                Trend Signals
            </div>
            """,
            unsafe_allow_html=True
        )

        latest_close = float(technical_data["Close"].iloc[-1])

        ma_periods = {
            "MA20": 20,
            "MA50": 50,
            "MA100": 100,
            "MA200": 200,
        }

        ma_cols = st.columns(4)

        for col, (ma_name, period) in zip(ma_cols, ma_periods.items()):
            ma_series = technical_data[ma_name].dropna()

            with col:
                if ma_series.empty:
                    st.metric(label=ma_name, value="N/A")
                    st.caption(f"Requires at least {period} trading days")
                else:
                    latest_ma = float(ma_series.iloc[-1])
                    difference = latest_close / latest_ma - 1

                    if latest_close > latest_ma:
                        signal = "Above"
                    elif latest_close < latest_ma:
                        signal = "Below"
                    else:
                        signal = "At MA"

                    st.metric(
                        label=ma_name,
                        value=f"{latest_ma:.2f}",
                        delta=f"{difference:+.2%}"
                    )
                    st.caption(f"Price is {signal.lower()} {ma_name}")

    
    # =====================================================
    # PERFORMANCE & DRAWDOWN
    # =====================================================

        st.write("")

        perf_left, perf_right = st.columns([1.5, 1])

        # -----------------------------------------------------
        # GROWTH OF $1
        # -----------------------------------------------------
        with perf_left:

            st.markdown("#### Growth of $1")

            wealth_fig = go.Figure()

            wealth_fig.add_trace(
                go.Scatter(
                    x=metrics["wealth"].index,
                    y=metrics["wealth"],
                    mode="lines",
                    name="Growth of $1",
                    line=dict(
                        width=2.3,
                        color="#8375ef"
                    )
                )
            )

            wealth_fig.update_layout(
                height=330,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                ),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                hovermode="x unified",
                xaxis=dict(
                    showgrid=False
                ),
                yaxis=dict(
                    gridcolor="#eef1f5"
                ),
                showlegend=False
            )

            st.plotly_chart(
                wealth_fig,
                use_container_width=True
            )


        # -----------------------------------------------------
        # DRAWDOWN
        # -----------------------------------------------------

        with perf_right:

            st.markdown("#### Drawdown")

            drawdown_fig = go.Figure()

            drawdown_fig.add_trace(
                go.Scatter(
                    x=metrics["drawdown"].index,
                    y=metrics["drawdown"],
                    mode="lines",
                    fill="tozeroy",
                    name="Drawdown",
                    line=dict(
                        width=2,
                        color="#ef767a"
                    )
                )
            )

            drawdown_fig.update_layout(
                height=330,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                hovermode="x unified",
                font=dict(
                    color="#5f6672",
                    size=12
                ),
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    linecolor="#edf0f4",
                    tickfont=dict(color="#8a919d")
                ),
                yaxis=dict(
                    gridcolor="#eef1f5",
                    zeroline=False,
                    linecolor="#edf0f4",
                    tickfont=dict(color="#8a919d"),
                    tickformat=".0%"
                ),
                showlegend=False
            )

            st.plotly_chart(
                drawdown_fig,
                use_container_width=True
            )    
        # =====================================================
        # SECOND ROW
        # =====================================================

        st.write("")

        lower_left, lower_right = st.columns(
            [1, 1.7]
        )


        # -----------------------------------------------------
        # RETURN DISTRIBUTION
        # -----------------------------------------------------

        with lower_left:

            st.markdown("#### Return Distribution")

            hist_fig = go.Figure()

            hist_fig.add_trace(
                go.Histogram(
                    x=metrics["returns"],
                    nbinsx=50,
                    marker_color="#9a8df6"
                )
            )

            hist_fig.update_layout(
                height=330,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(
                    color="#5f6672",
                    size=12
                ),
                xaxis=dict(
                    gridcolor="#eef1f5",
                    tickformat=".1%",
                    zeroline=False,
                    linecolor="#edf0f4",
                    tickfont=dict(color="#8a919d")
                ),
                yaxis=dict(
                    gridcolor="#eef1f5",
                    zeroline=False,
                    linecolor="#edf0f4",
                    tickfont=dict(color="#8a919d")
                ),
                showlegend=False
            )

            st.plotly_chart(
                hist_fig,
                use_container_width=True
            )
        
        # -----------------------------------------------------
        # ROLLING VOLATILITY
        # -----------------------------------------------------

        with lower_right:

            st.markdown("#### Rolling Risk")

            rolling_fig = go.Figure()

            rolling_fig.add_trace(
                go.Scatter(
                    x=metrics["rolling_vol"].index,
                    y=metrics["rolling_vol"],
                    mode="lines",
                    name="30-Day Rolling Volatility",
                    line=dict(
                        width=2.2,
                        color="#6fcf97"
                    )
                )
            )

            rolling_fig.update_layout(
                height=330,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                ),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                hovermode="x unified",
                font=dict(
                    color="#5f6672",
                    size=12
                ),
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    linecolor="#edf0f4",
                    tickfont=dict(
                        color="#8a919d"
                    )
                ),
                yaxis=dict(
                    gridcolor="#eef1f5",
                    tickformat=".0%",
                    zeroline=False,
                    linecolor="#edf0f4",
                    tickfont=dict(
                        color="#8a919d"
                    )
                ),
                showlegend=False
            )

            st.plotly_chart(
                rolling_fig,
                use_container_width=True
            )

            rolling_fig = go.Figure()

            rolling_fig.add_trace(
                go.Scatter(
                    x=metrics["rolling_vol"].index,
                    y=metrics["rolling_vol"],
                    mode="lines",
                    name="30-Day Rolling Volatility",
                    line=dict(
                        width=2.2,
                        color="#6fcf97"
                    )
                )
            )

            rolling_fig.update_layout(
                height=330,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                ),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                hovermode="x unified",
                xaxis=dict(
                    showgrid=False
                ),
                yaxis=dict(
                    gridcolor="#eef1f5",
                    tickformat=".0%"
                )
            )

            st.plotly_chart(
                rolling_fig,
                use_container_width=True
            )
            # =====================================================
        # DAILY RETURNS
        # =====================================================

        st.write("")

        st.markdown("#### Daily Return History")

        daily_fig = go.Figure()

        daily_fig.add_trace(
            go.Scatter(
                x=metrics["returns"].index,
                y=metrics["returns"],
                mode="lines",
                name="Daily Return",
                line=dict(
                    width=1.2,
                    color="#7c8da6"
                )
            )
        )

        daily_fig.add_hline(
            y=0,
            line_width=1,
            line_dash="dash"
        )

        daily_fig.update_layout(
            height=310,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            hovermode="x unified",
            xaxis=dict(
                showgrid=False
            ),
            yaxis=dict(
                gridcolor="#eef1f5",
                tickformat=".1%"
            ),
            showlegend=False
        )

        st.plotly_chart(
            daily_fig,
            use_container_width=True
        )

        # =====================================================
        # FOOTER CARD
        # =====================================================

        st.write("")

        st.markdown(
    """
    <div style="
    background:#ffffff;
    border:1px solid #e9edf3;
    border-radius:18px;
    padding:18px 22px;
    margin-top:8px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    ">

    <div>

    <div style="
    font-size:14px;
    font-weight:600;
    color:#202633;
    margin-bottom:5px;
    ">
    About MarketLens
    </div>

    <div style="
    font-size:13px;
    color:#8c94a0;
    line-height:1.5;
    ">
    Historical quantitative analytics for performance,
    risk and downside behavior.
    </div>

    </div>

    <div style="
    font-size:12px;
    color:#aaaeb7;
    background:#f6f7fa;
    padding:7px 11px;
    border-radius:10px;
    ">
    Educational analytics
    </div>

    </div>
    """,
    unsafe_allow_html=True
    )


elif section == "Overview / Single Asset":

    st.markdown(
        """
        <div class="ml-card">
            <div style="
                font-size: 20px;
                font-weight: 700;
                color: #202633;
                margin-bottom: 8px;
            ">
                Start an analysis
            </div>

            <div style="
                color: #7b8290;
                line-height: 1.6;
            ">
                Choose a ticker and analysis period from the left panel,
                then click <b>Analyze Asset</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
elif section == "Comparison & Diversification":

    st.caption(
        "Compare selected equities using matched trading dates, "
        "correlation, diversification and equal-weight portfolio metrics."
    )

    preset_assets = [
        "AAPL",
        "MSFT",
        "NVDA",
        "GOOGL",
        "AMZN",
        "META",
        "TSLA",
        "JPM",
        "V",
        "MA",
        "NFLX",
        "AMD",
        "INTC",
        "IBM",
        "ORCL",
        "CRM",
        "QCOM",
        "AVGO",
        "KSPI",
        "HSBK.IL",
        "KAP.IL"
    ]

    comparison_assets = st.multiselect(
        "Select assets",
        options=preset_assets,
        default=["AAPL", "MSFT", "NVDA"],
        max_selections=5,
    )

    custom_assets_input = st.text_input(
        "Add custom tickers",
        placeholder="e.g. KO, DIS, BABA, TSM"
    )

    custom_assets = [
        ticker.strip().upper()
        for ticker in custom_assets_input.split(",")
        if ticker.strip()
    ]

    comparison_assets = list(
        dict.fromkeys(
            comparison_assets + custom_assets
        )
    )

    if len(comparison_assets) > 5:
        st.warning(
            "Please compare no more than 5 assets at a time."
        )
        comparison_assets = comparison_assets[:5]




    
    if len(comparison_assets) < 2:

        st.info(
            "Select at least two assets to run the comparison."
        )

    else:

        price_series = []
        failed_assets = []

        with st.spinner(
            "Loading matched market data..."
        ):

            for asset in comparison_assets:

                asset_data = load_data(
                    asset,
                    start_date,
                    end_date
                )

                if asset_data is None:

                    failed_assets.append(asset)
                    continue

                asset_close = (
                    asset_data["Close"]
                    .dropna()
                    .rename(asset)
                )

                price_series.append(
                    asset_close
                )

        if failed_assets:

            st.warning(
                "No usable data were found for: "
                + ", ".join(failed_assets)
            )

        if len(price_series) < 2:

            st.error(
                "At least two assets with valid price data are required."
            )

        else:

            prices = pd.concat(
                price_series,
                axis=1,
                join="inner"
            ).dropna()

            if len(prices) < 30:

                st.error(
                    "The selected assets do not have enough "
                    "overlapping observations."
                )

            else:

                returns = (
                    prices
                    .pct_change()
                    .dropna()
                )

                correlation_matrix = (
                    returns.corr()
                )

                # =====================================================
                # AVERAGE PAIRWISE CORRELATION
                # =====================================================

                corr_values = []

                for i in range(
                    len(comparison_assets)
                ):

                    for j in range(
                        i + 1,
                        len(comparison_assets)
                    ):

                        asset_i = comparison_assets[i]
                        asset_j = comparison_assets[j]

                        if (
                            asset_i in returns.columns
                            and asset_j in returns.columns
                        ):

                            corr_values.append(
                                returns[
                                    asset_i
                                ].corr(
                                    returns[
                                        asset_j
                                    ]
                                )
                            )

                average_pairwise_corr = (
                    float(
                        np.mean(corr_values)
                    )
                    if corr_values
                    else np.nan
                )

                # =====================================================
                # EQUAL-WEIGHTED PORTFOLIO
                # =====================================================

                number_assets = (
                    returns.shape[1]
                )

                weights = np.repeat(
                    1 / number_assets,
                    number_assets
                )

                portfolio_returns = (
                    returns
                    .mul(
                        weights,
                        axis=1
                    )
                    .sum(axis=1)
                )

                portfolio_annual_return = (
                    portfolio_returns.mean()
                    * TRADING_DAYS
                )

                portfolio_annual_volatility = (
                    portfolio_returns.std()
                    * np.sqrt(
                        TRADING_DAYS
                    )
                )

                individual_volatility = (
                    returns.std()
                    * np.sqrt(
                        TRADING_DAYS
                    )
                )

                weighted_individual_volatility = (
                    individual_volatility
                    * weights
                ).sum()

                diversification_ratio = (
                    weighted_individual_volatility
                    / portfolio_annual_volatility
                    if portfolio_annual_volatility > 0
                    else np.nan
                )

                # =====================================================
                # KPI CARDS
                # =====================================================

                k1, k2, k3, k4 = (
                    st.columns(4)
                )

                k1.metric(
                    "Portfolio Return",
                    f"{portfolio_annual_return:.2%}"
                )

                k2.metric(
                    "Portfolio Volatility",
                    f"{portfolio_annual_volatility:.2%}"
                )

                k3.metric(
                    "Average Correlation",
                    f"{average_pairwise_corr:.3f}"
                )

                k4.metric(
                    "Diversification Ratio",
                    f"{diversification_ratio:.3f}"
                )

                st.caption(
                    f"Matched sample: "
                    f"{prices.index.min().date()} — "
                    f"{prices.index.max().date()} "
                    f"· {len(returns):,} daily-return observations"
                )

                st.write("")

                # =====================================================
                # CORRELATION MATRIX
                # =====================================================

                st.markdown(
                    "### Pairwise Correlation"
                )

                corr_fig = go.Figure(
                    data=go.Heatmap(
                        z=correlation_matrix.values,
                        x=correlation_matrix.columns,
                        y=correlation_matrix.index,
                        zmin=-1,
                        zmax=1,
                        colorscale="RdBu",
                        reversescale=True,
                        text=np.round(
                            correlation_matrix.values,
                            3
                        ),
                        texttemplate="%{text}",
                        hovertemplate=(
                            "%{y} vs %{x}"
                            "<br>Correlation: %{z:.3f}"
                            "<extra></extra>"
                        )
                    )
                )

                corr_fig.update_layout(
                    height=420,
                    margin=dict(
                        l=30,
                        r=30,
                        t=20,
                        b=20
                    ),
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff"
                )

                st.plotly_chart(
                    corr_fig,
                    use_container_width=True
                )

                # =====================================================
                # 30-DAY ROLLING CORRELATION
                # =====================================================

                st.markdown(
                    "### 30-Day Rolling Correlation"
                )

                rolling_corr_fig = (
                    go.Figure()
                )

                for i in range(
                    len(returns.columns)
                ):

                    for j in range(
                        i + 1,
                        len(returns.columns)
                    ):

                        asset_i = (
                            returns.columns[i]
                        )

                        asset_j = (
                            returns.columns[j]
                        )

                        rolling_corr = (
                            returns[asset_i]
                            .rolling(30)
                            .corr(
                                returns[asset_j]
                            )
                        )

                        rolling_corr_fig.add_trace(
                            go.Scatter(
                                x=rolling_corr.index,
                                y=rolling_corr,
                                mode="lines",
                                name=(
                                    f"{asset_i} / "
                                    f"{asset_j}"
                                ),
                                line=dict(
                                    width=2
                                )
                            )
                        )

                rolling_corr_fig.add_hline(
                    y=0,
                    line_width=1,
                    line_dash="dash"
                )

                rolling_corr_fig.update_layout(
                    height=380,
                    margin=dict(
                        l=20,
                        r=20,
                        t=20,
                        b=20
                    ),
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    hovermode="x unified",
                    yaxis=dict(
                        range=[-1, 1],
                        gridcolor="#eef1f5"
                    ),
                    xaxis=dict(
                        showgrid=False
                    )
                )

                st.plotly_chart(
                    rolling_corr_fig,
                    use_container_width=True
                )

                # =====================================================
                # EQUAL-WEIGHT PORTFOLIO GROWTH
                # =====================================================

                st.markdown(
                    "### Equal-Weighted Portfolio Growth"
                )

                portfolio_wealth = (
                    1 + portfolio_returns
                ).cumprod()

                portfolio_fig = (
                    go.Figure()
                )

                portfolio_fig.add_trace(
                    go.Scatter(
                        x=portfolio_wealth.index,
                        y=portfolio_wealth,
                        mode="lines",
                        name="Equal-Weighted Portfolio",
                        line=dict(
                            width=2.4
                        )
                    )
                )

                portfolio_fig.update_layout(
                    height=360,
                    margin=dict(
                        l=20,
                        r=20,
                        t=20,
                        b=20
                    ),
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    hovermode="x unified",
                    xaxis=dict(
                        showgrid=False
                    ),
                    yaxis=dict(
                        gridcolor="#eef1f5"
                    ),
                    showlegend=False
                )

                st.plotly_chart(
                    portfolio_fig,
                    use_container_width=True
                )

elif section == "Strategy Lab":


    st.caption(
        "Backtest moving-average trend-following strategies "
        "against a Buy & Hold benchmark."
    )

    strategy_ticker = st.text_input(
        "Strategy Ticker",
        value="AAPL"
    ).upper().strip()

    ma_window = st.selectbox(
        "Moving Average Window",
        [20, 50, 100, 200],
        index=3
    )

    if strategy_ticker:

        with st.spinner(
            f"Running strategy analysis for {strategy_ticker}..."
        ):

            strategy_data = load_data(
                strategy_ticker,
                start_date,
                end_date
            )

        if strategy_data is None:

            st.error(
                "No market data were found for this ticker."
            )

        else:

            strategy_close = (
                strategy_data["Close"]
                .dropna()
            )

            if len(strategy_close) <= ma_window + 1:

                st.error(
                    f"At least {ma_window + 2} observations "
                    f"are required for MA{ma_window}."
                )

            else:

                strategy_df = pd.DataFrame(
                    {"Close": strategy_close}
                )

                strategy_df["MA"] = (
                    strategy_df["Close"]
                    .rolling(ma_window)
                    .mean()
                )

                strategy_df["Return"] = (
                    strategy_df["Close"]
                    .pct_change()
                )

                # Signal:
                # 1 = price above moving average
                # 0 = price below moving average

                strategy_df["Signal"] = (
                    strategy_df["Close"]
                    > strategy_df["MA"]
                ).astype(int)

                # Lag position by one day to avoid look-ahead bias

                strategy_df["Position"] = (
                    strategy_df["Signal"]
                    .shift(1)
                )

                strategy_df["Strategy Return"] = (
                    strategy_df["Position"]
                    * strategy_df["Return"]
                )

                strategy_df = (
                    strategy_df
                    .dropna()
                )

                if strategy_df.empty:

                    st.error(
                        "No valid strategy observations were produced."
                    )

                else:

                    # ==============================================
                    # CUMULATIVE RETURNS
                    # ==============================================

                    strategy_df["Buy & Hold Wealth"] = (
                        1 + strategy_df["Return"]
                    ).cumprod()

                    strategy_df["Strategy Wealth"] = (
                        1
                        + strategy_df["Strategy Return"]
                    ).cumprod()

                    buy_hold_total_return = (
                        strategy_df[
                            "Buy & Hold Wealth"
                        ].iloc[-1]
                        - 1
                    )

                    strategy_total_return = (
                        strategy_df[
                            "Strategy Wealth"
                        ].iloc[-1]
                        - 1
                    )

                    # ==============================================
                    # ANNUALIZED RETURN / VOLATILITY
                    # ==============================================

                    buy_hold_annual_return = (
                        strategy_df["Return"].mean()
                        * TRADING_DAYS
                    )

                    strategy_annual_return = (
                        strategy_df[
                            "Strategy Return"
                        ].mean()
                        * TRADING_DAYS
                    )

                    buy_hold_volatility = (
                        strategy_df["Return"].std()
                        * np.sqrt(TRADING_DAYS)
                    )

                    strategy_volatility = (
                        strategy_df[
                            "Strategy Return"
                        ].std()
                        * np.sqrt(TRADING_DAYS)
                    )

                    # ==============================================
                    # SHARPE
                    # ==============================================

                    daily_rf = (
                        (1 + annual_rf)
                        ** (1 / TRADING_DAYS)
                        - 1
                    )

                    buy_hold_excess = (
                        strategy_df["Return"]
                        - daily_rf
                    )

                    strategy_excess = (
                        strategy_df[
                            "Strategy Return"
                        ]
                        - daily_rf
                    )

                    buy_hold_sharpe = (
                        buy_hold_excess.mean()
                        / buy_hold_excess.std()
                        * np.sqrt(TRADING_DAYS)
                        if buy_hold_excess.std() > 0
                        else np.nan
                    )

                    strategy_sharpe = (
                        strategy_excess.mean()
                        / strategy_excess.std()
                        * np.sqrt(TRADING_DAYS)
                        if strategy_excess.std() > 0
                        else np.nan
                    )

                    # ==============================================
                    # MAXIMUM DRAWDOWN
                    # ==============================================

                    buy_hold_peak = (
                        strategy_df[
                            "Buy & Hold Wealth"
                        ].cummax()
                    )

                    strategy_peak = (
                        strategy_df[
                            "Strategy Wealth"
                        ].cummax()
                    )

                    buy_hold_drawdown = (
                        strategy_df[
                            "Buy & Hold Wealth"
                        ]
                        / buy_hold_peak
                        - 1
                    )

                    strategy_drawdown = (
                        strategy_df[
                            "Strategy Wealth"
                        ]
                        / strategy_peak
                        - 1
                    )

                    buy_hold_mdd = (
                        buy_hold_drawdown.min()
                    )

                    strategy_mdd = (
                        strategy_drawdown.min()
                    )

                    # ==============================================
                    # KPI CARDS
                    # ==============================================

                    st.markdown(
                        f"### MA{ma_window} Strategy"
                    )

                    s1, s2, s3, s4 = (
                        st.columns(4)
                    )

                    s1.metric(
                        "Strategy Total Return",
                        f"{strategy_total_return:.2%}"
                    )

                    s2.metric(
                        "Strategy Volatility",
                        f"{strategy_volatility:.2%}"
                    )

                    s3.metric(
                        "Strategy Sharpe",
                        f"{strategy_sharpe:.3f}"
                    )

                    s4.metric(
                        "Strategy Max Drawdown",
                        f"{strategy_mdd:.2%}"
                    )

                    st.write("")

                    # ==============================================
                    # BUY & HOLD VS STRATEGY
                    # ==============================================

                    st.markdown(
                        "### Strategy vs Buy & Hold"
                    )

                    wealth_fig = go.Figure()

                    wealth_fig.add_trace(
                        go.Scatter(
                            x=strategy_df.index,
                            y=strategy_df[
                                "Buy & Hold Wealth"
                            ],
                            mode="lines",
                            name="Buy & Hold",
                            line=dict(
                                width=2.2
                            )
                        )
                    )

                    wealth_fig.add_trace(
                        go.Scatter(
                            x=strategy_df.index,
                            y=strategy_df[
                                "Strategy Wealth"
                            ],
                            mode="lines",
                            name=f"MA{ma_window} Strategy",
                            line=dict(
                                width=2.2
                            )
                        )
                    )

                    wealth_fig = apply_chart_style(
                        wealth_fig,
                        height=360,
                        showlegend=True
                    )

                    st.plotly_chart(
                        wealth_fig,
                        use_container_width=True
                    )

                    # ==============================================
                    # PRICE + MOVING AVERAGE
                    # ==============================================

                    st.markdown(
                        f"### Price vs MA{ma_window}"
                    )

                    price_ma_fig = go.Figure()

                    price_ma_fig.add_trace(
                        go.Scatter(
                            x=strategy_df.index,
                            y=strategy_df["Close"],
                            mode="lines",
                            name="Close",
                            line=dict(
                                width=2
                            )
                        )
                    )

                    price_ma_fig.add_trace(
                        go.Scatter(
                            x=strategy_df.index,
                            y=strategy_df["MA"],
                            mode="lines",
                            name=f"MA{ma_window}",
                            line=dict(
                                width=2
                            )
                        )
                    )
                    price_ma_fig = apply_chart_style(
                        price_ma_fig,
                        height=360,
                        showlegend=True
                    )
                    st.plotly_chart(
                        price_ma_fig,
                        use_container_width=True
                    )
                    

                    # ==============================================
                    # COMPARISON TABLE
                    # ==============================================

                    st.markdown(
                        "### Performance Comparison"
                    )

                    comparison_table = pd.DataFrame(
                        {
                            "Metric": [
                                "Total Return",
                                "Annualized Return",
                                "Annualized Volatility",
                                "Sharpe Ratio",
                                "Maximum Drawdown"
                            ],
                            "Buy & Hold": [
                                f"{buy_hold_total_return:.2%}",
                                f"{buy_hold_annual_return:.2%}",
                                f"{buy_hold_volatility:.2%}",
                                f"{buy_hold_sharpe:.3f}",
                                f"{buy_hold_mdd:.2%}"
                            ],
                            f"MA{ma_window} Strategy": [
                                f"{strategy_total_return:.2%}",
                                f"{strategy_annual_return:.2%}",
                                f"{strategy_volatility:.2%}",
                                f"{strategy_sharpe:.3f}",
                                f"{strategy_mdd:.2%}"
                            ]
                        }
                    )

                    st.dataframe(
                        comparison_table,
                        use_container_width=True,
                        hide_index=True
                    )


elif section == "Costs & Robustness":

    st.markdown("## Costs & Robustness")

    st.caption(
        "Evaluate whether moving-average strategy results remain robust "
        "after transaction costs and across additional performance diagnostics."
    )

    robustness_ticker = st.text_input(
        "Robustness Ticker",
        value="AAPL"
    ).upper().strip()

    robustness_ma = st.selectbox(
        "Strategy MA Window",
        [20, 50, 100, 200],
        index=3,
        key="robustness_ma"
    )

    if robustness_ticker:

        with st.spinner(
            f"Running robustness analysis for {robustness_ticker}..."
        ):

            robustness_data = load_data(
                robustness_ticker,
                start_date,
                end_date
            )

        if robustness_data is None:

            st.error(
                "No market data were found for this ticker."
            )

        else:

            robustness_close = (
                robustness_data["Close"]
                .dropna()
            )

            if len(robustness_close) <= robustness_ma + 1:

                st.error(
                    f"At least {robustness_ma + 2} observations "
                    f"are required for MA{robustness_ma}."
                )

            else:

                robustness_df = pd.DataFrame(
                    {"Close": robustness_close}
                )

                robustness_df["MA"] = (
                    robustness_df["Close"]
                    .rolling(robustness_ma)
                    .mean()
                )

                robustness_df["Return"] = (
                    robustness_df["Close"]
                    .pct_change()
                )

                robustness_df["Signal"] = (
                    robustness_df["Close"]
                    > robustness_df["MA"]
                ).astype(int)

                robustness_df["Position"] = (
                    robustness_df["Signal"]
                    .shift(1)
                )

                robustness_df["Gross Strategy Return"] = (
                    robustness_df["Position"]
                    * robustness_df["Return"]
                )

                robustness_df = (
                    robustness_df
                    .dropna()
                )

                if robustness_df.empty:

                    st.error(
                        "No valid strategy observations were produced."
                    )

                else:

                    # ==============================================
                    # POSITION CHANGES / TURNOVER
                    # ==============================================

                    robustness_df["Position Change"] = (
                        robustness_df["Position"]
                        .diff()
                        .abs()
                        .fillna(0)
                    )

                    position_changes = (
                        robustness_df["Position Change"]
                        .sum()
                    )

                    # ==============================================
                    # TRANSACTION COST SCENARIOS
                    # ==============================================

                    cost_scenarios_bps = [
                        0,
                        10,
                        25
                    ]

                    cost_results = []

                    for cost_bps in cost_scenarios_bps:

                        cost_rate = (
                            cost_bps / 10000
                        )

                        robustness_df[
                            f"Net Return {cost_bps}bps"
                        ] = (
                            robustness_df[
                                "Gross Strategy Return"
                            ]
                            - (
                                robustness_df[
                                    "Position Change"
                                ]
                                * cost_rate
                            )
                        )

                        robustness_df[
                            f"Wealth {cost_bps}bps"
                        ] = (
                            1
                            + robustness_df[
                                f"Net Return {cost_bps}bps"
                            ]
                        ).cumprod()

                        total_return = (
                            robustness_df[
                                f"Wealth {cost_bps}bps"
                            ].iloc[-1]
                            - 1
                        )

                        annual_return = (
                            robustness_df[
                                f"Net Return {cost_bps}bps"
                            ].mean()
                            * TRADING_DAYS
                        )

                        annual_volatility = (
                            robustness_df[
                                f"Net Return {cost_bps}bps"
                            ].std()
                            * np.sqrt(TRADING_DAYS)
                        )

                        daily_rf = (
                            (1 + annual_rf)
                            ** (1 / TRADING_DAYS)
                            - 1
                        )

                        excess_returns = (
                            robustness_df[
                                f"Net Return {cost_bps}bps"
                            ]
                            - daily_rf
                        )

                        sharpe = (
                            excess_returns.mean()
                            / excess_returns.std()
                            * np.sqrt(TRADING_DAYS)
                            if excess_returns.std() > 0
                            else np.nan
                        )

                        wealth_series = (
                            robustness_df[
                                f"Wealth {cost_bps}bps"
                            ]
                        )

                        peak = (
                            wealth_series.cummax()
                        )

                        drawdown = (
                            wealth_series / peak - 1
                        )

                        max_drawdown = (
                            drawdown.min()
                        )

                        cost_results.append(
                            {
                                "Cost (bps)": cost_bps,
                                "Total Return": total_return,
                                "Annualized Return": annual_return,
                                "Annualized Volatility": annual_volatility,
                                "Sharpe Ratio": sharpe,
                                "Maximum Drawdown": max_drawdown
                            }
                        )

                    # ==============================================
                    # BUY & HOLD BENCHMARK
                    # ==============================================

                    robustness_df["Buy & Hold Wealth"] = (
                        1 + robustness_df["Return"]
                    ).cumprod()

                    buy_hold_total_return = (
                        robustness_df[
                            "Buy & Hold Wealth"
                        ].iloc[-1]
                        - 1
                    )

                    buy_hold_annual_return = (
                        robustness_df["Return"].mean()
                        * TRADING_DAYS
                    )

                    # ==============================================
                    # RETURN LOSS FROM COSTS
                    # ==============================================

                    gross_total_return = (
                        cost_results[0][
                            "Total Return"
                        ]
                    )

                    return_loss_10 = (
                        gross_total_return
                        - cost_results[1][
                            "Total Return"
                        ]
                    )

                    return_loss_25 = (
                        gross_total_return
                        - cost_results[2][
                            "Total Return"
                        ]
                    )

                    # ==============================================
                    # ANNUAL OUTPERFORMANCE
                    # ==============================================

                    gross_annual_return = (
                        cost_results[0][
                            "Annualized Return"
                        ]
                    )

                    annual_outperformance = (
                        gross_annual_return
                        - buy_hold_annual_return
                    )

                    # ==============================================
                    # WIN RATE
                    # ==============================================

                    active_days = (
                        robustness_df[
                            "Position"
                        ] > 0
                    )

                    active_strategy_returns = (
                        robustness_df.loc[
                            active_days,
                            "Gross Strategy Return"
                        ]
                    )

                    win_rate = (
                        (
                            active_strategy_returns
                            > 0
                        ).mean()
                        if len(
                            active_strategy_returns
                        ) > 0
                        else np.nan
                    )

                    # ==============================================
                    # DOWNSIDE PROTECTION
                    # ==============================================

                    negative_market_days = (
                        robustness_df[
                            "Return"
                        ] < 0
                    )

                    buy_hold_downside_loss = (
                        robustness_df.loc[
                            negative_market_days,
                            "Return"
                        ].abs().sum()
                    )

                    strategy_downside_loss = (
                        robustness_df.loc[
                            negative_market_days,
                            "Gross Strategy Return"
                        ].abs().sum()
                    )

                    downside_protection = (
                        1
                        - (
                            strategy_downside_loss
                            / buy_hold_downside_loss
                        )
                        if buy_hold_downside_loss > 0
                        else np.nan
                    )

                    # ==============================================
                    # KPI CARDS
                    # ==============================================

                    r1, r2, r3, r4 = (
                        st.columns(4)
                    )

                    r1.metric(
                        "Position Changes",
                        f"{position_changes:.0f}"
                    )

                    r2.metric(
                        "Annual Outperformance",
                        f"{annual_outperformance:+.2%}"
                    )

                    r3.metric(
                        "Win Rate",
                        f"{win_rate:.2%}"
                    )

                    r4.metric(
                        "Downside Protection",
                        f"{downside_protection:.2%}"
                    )

                    st.write("")

                    # ==============================================
                    # TRANSACTION COST IMPACT
                    # ==============================================

                    st.markdown(
                        "### Transaction Cost Impact"
                    )

                    cost_fig = go.Figure()

                    for cost_bps in cost_scenarios_bps:

                        cost_fig.add_trace(
                            go.Scatter(
                                x=robustness_df.index,
                                y=robustness_df[
                                    f"Wealth {cost_bps}bps"
                                ],
                                mode="lines",
                                name=f"{cost_bps} bps",
                                line=dict(
                                    width=2.2
                                )
                            )
                        )

                    cost_fig = apply_chart_style(
                        cost_fig,
                        height=390,
                        showlegend=True
                    )
                    # ==============================================
                    # COST SUMMARY CARDS
                    # ==============================================

                    c1, c2 = st.columns(2)

                    c1.metric(
                        "Return Loss at 10 bps",
                        f"{return_loss_10:.2%}"
                    )

                    c2.metric(
                        "Return Loss at 25 bps",
                        f"{return_loss_25:.2%}"
                    )

                    st.write("")

                    # ==============================================
                    # ROBUSTNESS TABLE
                    # ==============================================

                    st.markdown(
                        "### Robustness Summary"
                    )

                    robustness_table = (
                        pd.DataFrame(
                            cost_results
                        )
                    )

                    robustness_table[
                        "Total Return"
                    ] = robustness_table[
                        "Total Return"
                    ].map(
                        lambda x: f"{x:.2%}"
                    )

                    robustness_table[
                        "Annualized Return"
                    ] = robustness_table[
                        "Annualized Return"
                    ].map(
                        lambda x: f"{x:.2%}"
                    )

                    robustness_table[
                        "Annualized Volatility"
                    ] = robustness_table[
                        "Annualized Volatility"
                    ].map(
                        lambda x: f"{x:.2%}"
                    )

                    robustness_table[
                        "Sharpe Ratio"
                    ] = robustness_table[
                        "Sharpe Ratio"
                    ].map(
                        lambda x: f"{x:.3f}"
                    )

                    robustness_table[
                        "Maximum Drawdown"
                    ] = robustness_table[
                        "Maximum Drawdown"
                    ].map(
                        lambda x: f"{x:.2%}"
                    )

                    st.dataframe(
                        robustness_table,
                        use_container_width=True,
                        hide_index=True
                    )
elif section == "Methodology":

    st.caption(
        "MarketLens uses transparent quantitative methods for return, "
        "risk, diversification and trend-following analysis."
    )

    # =====================================================
    # DATA & SAMPLE CONSTRUCTION
    # =====================================================

    st.markdown("### 1. Data & Sample Construction")

    st.markdown(
        """
        MarketLens uses historical daily market data downloaded through Yahoo Finance.

        For multi-asset comparisons, only dates shared by all selected assets are retained.
        This matched-sample approach avoids comparing securities over different trading periods.

        The default annualization convention is:

        - 252 trading days per year
        - Daily arithmetic returns
        - Annualized arithmetic return = mean daily return × 252
        - Annualized volatility = daily return standard deviation × √252
        """
    )

    # =====================================================
    # RETURN METRICS
    # =====================================================

    st.markdown("### 2. Return Metrics")

    st.latex(
        r"r_t = \frac{P_t}{P_{t-1}} - 1"
    )

    st.markdown(
        """
        where \(P_t\) is the closing price at time \(t\).

        Cumulative wealth is calculated as:
        """
    )

    st.latex(
        r"W_t = \prod_{i=1}^{t}(1+r_i)"
    )

    st.markdown(
        """
        Total cumulative return is therefore:
        """
    )

    st.latex(
        r"R_{cum} = W_T - 1"
    )

    # =====================================================
    # RISK METRICS
    # =====================================================

    st.markdown("### 3. Risk Metrics")

    st.markdown(
        """
        MarketLens reports both static and time-varying risk measures.

        **Annualized volatility**
        """
    )

    st.latex(
        r"\sigma_{ann} = \sigma_{daily}\sqrt{252}"
    )

    st.markdown(
        """
        **30-Day Rolling Annualized Volatility**
        """
    )

    st.latex(
        r"\sigma_{30,t} = SD(r_{t-29},...,r_t)\sqrt{252}"
    )

    st.markdown(
        """
        **Drawdown**
        """
    )

    st.latex(
        r"D_t = \frac{W_t}{\max_{s \leq t} W_s} - 1"
    )

    st.markdown(
        """
        Maximum Drawdown is the minimum value of the drawdown series.
        """
    )

    # =====================================================
    # SHARPE RATIO
    # =====================================================

    st.markdown("### 4. Risk-Adjusted Performance")

    st.markdown(
        """
        The Sharpe Ratio uses an annual risk-free rate supplied by the user.

        The annual rate is converted into an equivalent daily rate:
        """
    )

    st.latex(
        r"r_{f,daily} = (1+r_{f,annual})^{1/252} - 1"
    )

    st.markdown(
        """
        The annualized Sharpe Ratio is:
        """
    )

    st.latex(
        r"Sharpe = \frac{\overline{r-r_f}}{SD(r-r_f)}\sqrt{252}"
    )

    # =====================================================
    # CORRELATION & DIVERSIFICATION
    # =====================================================

    st.markdown("### 5. Correlation & Diversification")

    st.markdown(
        """
        Pairwise correlation measures the degree to which asset returns move together.

        For a portfolio of \(N\) assets, Average Pairwise Correlation is calculated
        using all unique asset pairs.
        """
    )

    st.latex(
    r"\bar{\rho} = \frac{2}{N(N-1)} \sum_{i<j}\rho_{ij}"
    )

    st.markdown(
        """
        Equal-weight portfolio returns are calculated using:
        """
    )

    st.latex(
        r"r_{p,t} = \sum_{i=1}^{N} w_i r_{i,t}"
    )

    st.markdown(
        """
        where:
        """
    )

    st.latex(
        r"w_i = \frac{1}{N}"
    )

    st.markdown(
        """
        The Diversification Ratio is:
        """
    )

    st.latex(
    r"DR = \frac{\sum_{i=1}^{N} w_i \sigma_i}{\sigma_p}"
    )

    st.markdown(
        """
        A value above 1 indicates that portfolio volatility is lower than
        the weighted average volatility of its components.
        """
    )

    # =====================================================
    # TREND-FOLLOWING STRATEGY
    # =====================================================

    st.markdown("### 6. Moving-Average Trend-Following")

    st.markdown(
        """
        MarketLens evaluates moving-average rules using MA20, MA50, MA100 and MA200.

        The basic signal is:
        """
    )

    st.latex(
    r"Signal_t = \begin{cases} 1, & P_t > MA_t \\ 0, & P_t \leq MA_t \end{cases}"
    )

    st.markdown(
        """
        To avoid look-ahead bias, the trading position is lagged by one trading day:
        """
    )

    st.latex(
        r"Position_t = Signal_{t-1}"
    )

    st.markdown(
        """
        Strategy return is therefore:
        """
    )

    st.latex(
    r"r_{strategy,t} = Position_t \times r_t"
    )
    st.markdown(
        """
        Buy & Hold is used as the benchmark over the same valid evaluation period.
        """
    )

    # =====================================================
    # TRANSACTION COSTS
    # =====================================================

    st.markdown("### 7. Transaction Costs")

    st.markdown(
        """
        Robustness tests evaluate three one-way transaction-cost assumptions:

        - 0 basis points
        - 10 basis points
        - 25 basis points

        A cost is applied whenever the position changes.
        """
    )

    st.latex(
    r"Turnover_t = |Position_t - Position_{t-1}|"
)
    st.latex(
    r"r_{net,t} = r_{gross,t} - Turnover_t \times Cost"
    )
   
    # =====================================================
    # ROBUSTNESS METRICS
    # =====================================================

    st.markdown("### 8. Robustness Metrics")

    st.markdown(
        """
        **Position Changes / Turnover**  
        Measures how frequently the strategy moves into or out of the market.

        **Return Loss from Transaction Costs**  
        Difference between gross strategy return and net return after costs.

        **Annual Strategy Outperformance**  
        Difference between annualized strategy return and annualized Buy & Hold return.

        **Win Rate**  
        Fraction of active strategy days with positive strategy returns.

        **Downside Protection**  
        Measures how much negative-market-day loss is reduced by the strategy relative
        to Buy & Hold.
        """
    )

    # =====================================================
    # IMPORTANT ASSUMPTIONS
    # =====================================================

    st.markdown("### 9. Key Assumptions")

    st.markdown(
        """
        MarketLens is intentionally designed as a transparent research tool rather than
        a production trading engine.

        The current implementation assumes:

        - Close-to-close daily returns
        - Long-or-cash strategy positions only
        - No leverage
        - No short selling
        - No slippage
        - No bid-ask spread modelling
        - No taxes
        - No market-impact modelling
        - Constant transaction-cost assumptions
        - Historical results do not imply future performance
        """
    )

    # =====================================================
    # LIMITATIONS
    # =====================================================

    st.markdown("### 10. Limitations")

    st.markdown(
        """
        Results depend on the selected securities, date range and market regime.

        Correlation and volatility are not stable through time, and moving-average
        strategies may perform differently across assets and periods.

        Kazakhstan-related securities included in MarketLens should not be interpreted
        as a complete representation of the Kazakhstan equity market.

        MarketLens is intended for educational and research purposes only and should not
        be interpreted as investment advice.
        """
    )


