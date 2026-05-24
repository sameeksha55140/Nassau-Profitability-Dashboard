
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Nassau Candy Dashboard",
    layout="wide"
)

# =====================================================
# TITLE
# =====================================================

st.title("🍭 Nassau Candy Distributor Dashboard")
st.markdown("## Product Line Profitability & Margin Performance Analysis")

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv("Nassau Candy Distributor.csv")

# =====================================================
# DATA CLEANING
# =====================================================

# Safe date conversion
df['Order Date'] = pd.to_datetime(
    df['Order Date'],
    errors='coerce'
)

# Remove invalid dates
df = df.dropna(subset=['Order Date'])

# Remove invalid sales
df = df[df['Sales'] > 0]

# Fill missing units
df['Units'] = df['Units'].fillna(1)

# =====================================================
# KPI CALCULATIONS
# =====================================================

# Gross Margin %
df['Gross Margin %'] = (
    df['Gross Profit'] / df['Sales']
) * 100

# Profit Per Unit
df['Profit per Unit'] = (
    df['Gross Profit'] / df['Units']
)

# Revenue Contribution %
total_sales = df['Sales'].sum()

df['Revenue Contribution %'] = (
    df['Sales'] / total_sales
) * 100

# Profit Contribution %
total_profit = df['Gross Profit'].sum()

df['Profit Contribution %'] = (
    df['Gross Profit'] / total_profit
) * 100

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("🔍 Dashboard Filters")

# Date Range Selector
start_date, end_date = st.sidebar.date_input(
    "📅 Select Date Range",
    [
        df['Order Date'].min(),
        df['Order Date'].max()
    ]
)

# Division Filter
division = st.sidebar.selectbox(
    "🏭 Select Division",
    ["All"] + list(df['Division'].unique())
)

# Margin Threshold Slider
margin_filter = st.sidebar.slider(
    "📈 Minimum Gross Margin %",
    min_value=0,
    max_value=100,
    value=10
)

# Product Search
product_search = st.sidebar.text_input(
    "🔎 Search Product"
)

# =====================================================
# APPLY FILTERS
# =====================================================

filtered_df = df.copy()

# Date Filter
filtered_df = filtered_df[
    (filtered_df['Order Date'] >= pd.to_datetime(start_date)) &
    (filtered_df['Order Date'] <= pd.to_datetime(end_date))
]

# Division Filter
if division != "All":
    filtered_df = filtered_df[
        filtered_df['Division'] == division
    ]

# Margin Filter
filtered_df = filtered_df[
    filtered_df['Gross Margin %'] >= margin_filter
]

# Product Search Filter
if product_search:
    filtered_df = filtered_df[
        filtered_df['Product Name']
        .str.contains(product_search, case=False)
    ]

# =====================================================
# KPI CARDS
# =====================================================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Sales",
        f"${filtered_df['Sales'].sum():,.0f}"
    )

with col2:
    st.metric(
        "Total Gross Profit",
        f"${filtered_df['Gross Profit'].sum():,.0f}"
    )

with col3:
    st.metric(
        "Average Margin %",
        f"{filtered_df['Gross Margin %'].mean():.2f}%"
    )

with col4:
    st.metric(
        "Products",
        filtered_df['Product Name'].nunique()
    )

# =====================================================
# PRODUCT PROFITABILITY OVERVIEW
# =====================================================

st.markdown("---")
st.header("🏆 Product Profitability Overview")

# Product Margin Leaderboard
top_margin = (
    filtered_df.groupby('Product Name')['Gross Margin %']
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig1 = px.bar(
    top_margin,
    x='Product Name',
    y='Gross Margin %',
    color='Gross Margin %',
    title='Top 10 Products by Gross Margin %'
)

st.plotly_chart(fig1, width='stretch')

# Profit Contribution Chart
profit_contribution = (
    filtered_df.groupby('Product Name')['Gross Profit']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig2 = px.pie(
    profit_contribution,
    names='Product Name',
    values='Gross Profit',
    title='Profit Contribution by Product'
)

st.plotly_chart(fig2, width='stretch')

# =====================================================
# DIVISION PERFORMANCE DASHBOARD
# =====================================================

st.markdown("---")
st.header("🏭 Division Performance Dashboard")

division_summary = (
    filtered_df.groupby('Division')
    .agg({
        'Sales': 'sum',
        'Gross Profit': 'sum',
        'Gross Margin %': 'mean'
    })
    .reset_index()
)

# Revenue vs Profit Comparison
fig3 = px.bar(
    division_summary,
    x='Division',
    y=['Sales', 'Gross Profit'],
    barmode='group',
    title='Revenue vs Gross Profit by Division'
)

st.plotly_chart(fig3, width='stretch')

# Margin Distribution
fig4 = px.box(
    filtered_df,
    x='Division',
    y='Gross Margin %',
    color='Division',
    title='Margin Distribution by Division'
)

st.plotly_chart(fig4, width='stretch')

# =====================================================
# COST VS MARGIN DIAGNOSTICS
# =====================================================

st.markdown("---")
st.header("⚠️ Cost vs Margin Diagnostics")

# Cost-Sales Scatter Plot
fig5 = px.scatter(
    filtered_df,
    x='Cost',
    y='Sales',
    size='Gross Profit',
    color='Gross Margin %',
    hover_data=['Product Name'],
    title='Cost vs Sales Scatter Analysis'
)

st.plotly_chart(fig5, width='stretch')

# Margin Risk Flags
st.subheader("🚨 Margin Risk Products")

risk_products = filtered_df[
    filtered_df['Gross Margin %'] < 10
]

st.dataframe(
    risk_products[
        [
            'Product Name',
            'Division',
            'Sales',
            'Cost',
            'Gross Profit',
            'Gross Margin %'
        ]
    ],
    width='stretch'
)

# =====================================================
# PROFIT CONCENTRATION ANALYSIS
# =====================================================

st.markdown("---")
st.header("📈 Profit Concentration Analysis")

pareto = (
    filtered_df.groupby('Product Name')['Gross Profit']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

pareto['Cumulative Profit %'] = (
    pareto['Gross Profit'].cumsum()
    / pareto['Gross Profit'].sum()
) * 100

# Pareto Chart
fig6 = go.Figure()

fig6.add_trace(
    go.Bar(
        x=pareto['Product Name'],
        y=pareto['Gross Profit'],
        name='Gross Profit'
    )
)

fig6.add_trace(
    go.Scatter(
        x=pareto['Product Name'],
        y=pareto['Cumulative Profit %'],
        name='Cumulative Profit %',
        yaxis='y2'
    )
)

fig6.update_layout(
    title='Pareto Analysis',
    yaxis=dict(
        title='Gross Profit'
    ),
    yaxis2=dict(
        title='Cumulative Profit %',
        overlaying='y',
        side='right'
    )
)

st.plotly_chart(fig6, width='stretch')

# =====================================================
# DEPENDENCY INDICATORS
# =====================================================

st.markdown("---")
st.header("⚡ Dependency Indicators")

top_dependency = pareto.head(5)

st.write(
    "Top products contributing the highest share of total profit."
)

st.dataframe(
    top_dependency[
        ['Product Name', 'Gross Profit']
    ],
    width='stretch'
)

# =====================================================
# FILTERED DATASET
# =====================================================

st.markdown("---")
st.header("📋 Filtered Dataset")

st.dataframe(
    filtered_df,
    width='stretch'
)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")
st.markdown(
    "Developed using Python, Pandas, Plotly, and Streamlit 🚀"
)
