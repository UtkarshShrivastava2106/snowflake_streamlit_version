import streamlit as st
import pandas as pd


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Orders & Refund Dashboard",
    page_icon="💰",
    layout="wide",
)


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

# Change this value when creating the PROD Streamlit app.
#
# NON-PROD:
# DB_G_GIT_UAT
#
# PROD:
# DB_G_PROD

DATABASE = "DB_G_GIT_UAT"

SCHEMA = "FINANCE"
TABLE = "ORDERS"

FULL_TABLE_NAME = f"{DATABASE}.{SCHEMA}.{TABLE}"


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

conn = st.connection(
    "snowflake",
    type="snowflake",
)

session = conn.session()


# ============================================================
# HEADER
# ============================================================

st.title("💰 Orders & Refund Dashboard")

st.caption(
    f"Environment: {'NON-PROD' if DATABASE == 'DB_G_GIT_UAT' else 'PROD'}"
    f" | Source: {FULL_TABLE_NAME}"
)


# ============================================================
# DATE RANGE
# ============================================================

date_query = f"""
SELECT
    MIN(CREATED_AT) AS MIN_DATE,
    MAX(CREATED_AT) AS MAX_DATE
FROM {FULL_TABLE_NAME}
"""

date_result = session.sql(date_query).collect()[0]

min_date = date_result["MIN_DATE"]
max_date = date_result["MAX_DATE"]


st.sidebar.header("🔎 Filters")


if min_date and max_date:

    start_date = st.sidebar.date_input(
        "Start Date",
        value=min_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

    end_date = st.sidebar.date_input(
        "End Date",
        value=max_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

else:

    start_date = None
    end_date = None


# ============================================================
# FILTER
# ============================================================

if start_date and end_date:

    where_clause = f"""
        WHERE CREATED_AT >= '{start_date}'
        AND CREATED_AT < DATEADD(
            DAY,
            1,
            '{end_date}'
        )
    """

else:

    where_clause = ""


# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📌 Key Metrics")


kpi_query = f"""
SELECT

    COUNT(DISTINCT ORDER_ID) AS TOTAL_ORDERS,

    COUNT(DISTINCT ORDER_ITEM_ID) AS REFUND_ITEMS,

    COALESCE(
        SUM(REFUND_AMOUNT_USD),
        0
    ) AS TOTAL_REFUND,

    COALESCE(
        AVG(REFUND_AMOUNT_USD),
        0
    ) AS AVG_REFUND

FROM {FULL_TABLE_NAME}

{where_clause}
"""


kpi = session.sql(kpi_query).collect()[0]


total_orders = kpi["TOTAL_ORDERS"]
refund_items = kpi["REFUND_ITEMS"]
total_refund = float(kpi["TOTAL_REFUND"] or 0)
avg_refund = float(kpi["AVG_REFUND"] or 0)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Orders",
        f"{total_orders:,}",
    )


with col2:

    st.metric(
        "Refund Items",
        f"{refund_items:,}",
    )


with col3:

    st.metric(
        "Total Refund",
        f"${total_refund:,.2f}",
    )


with col4:

    st.metric(
        "Average Refund",
        f"${avg_refund:,.2f}",
    )


# ============================================================
# MONTHLY TREND
# ============================================================

st.subheader("📈 Refund Trend")


trend_query = f"""
SELECT

    DATE_TRUNC(
        'MONTH',
        CREATED_AT
    ) AS MONTH,

    COUNT(DISTINCT ORDER_ID) AS ORDER_COUNT,

    COUNT(DISTINCT ORDER_ITEM_ID) AS REFUND_ITEMS,

    SUM(REFUND_AMOUNT_USD) AS REFUND_AMOUNT

FROM {FULL_TABLE_NAME}

{where_clause}

GROUP BY 1

ORDER BY 1
"""


trend_df = (
    session.sql(trend_query)
    .to_pandas()
)


if not trend_df.empty:

    trend_df["MONTH"] = pd.to_datetime(
        trend_df["MONTH"]
    )

    trend_df = trend_df.set_index("MONTH")

    st.line_chart(
        trend_df["REFUND_AMOUNT"],
        x_label="Month",
        y_label="Refund Amount (USD)",
    )

else:

    st.info(
        "No refund data available for the selected period."
    )


# ============================================================
# TWO CHARTS
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Refund Items
# ------------------------------------------------------------

with col1:

    st.subheader("📊 Refund Items by Month")

    if not trend_df.empty:

        st.bar_chart(
            trend_df["REFUND_ITEMS"],
            x_label="Month",
            y_label="Refund Items",
        )


# ------------------------------------------------------------
# Orders
# ------------------------------------------------------------

with col2:

    st.subheader("📦 Orders by Month")

    if not trend_df.empty:

        st.bar_chart(
            trend_df["ORDER_COUNT"],
            x_label="Month",
            y_label="Orders",
        )


# ============================================================
# REFUND AMOUNT DISTRIBUTION
# ============================================================

st.subheader("💵 Refund Amount Distribution")


distribution_query = f"""
SELECT
    REFUND_AMOUNT_USD
FROM {FULL_TABLE_NAME}

{where_clause}

AND REFUND_AMOUNT_USD IS NOT NULL

LIMIT 10000
"""


if where_clause:

    distribution_query = f"""
    SELECT
        REFUND_AMOUNT_USD
    FROM {FULL_TABLE_NAME}

    {where_clause}

    AND REFUND_AMOUNT_USD IS NOT NULL

    LIMIT 10000
    """

else:

    distribution_query = f"""
    SELECT
        REFUND_AMOUNT_USD
    FROM {FULL_TABLE_NAME}

    WHERE REFUND_AMOUNT_USD IS NOT NULL

    LIMIT 10000
    """


distribution_df = (
    session.sql(distribution_query)
    .to_pandas()
)


if not distribution_df.empty:

    distribution_df = distribution_df.rename(
        columns={
            "REFUND_AMOUNT_USD": "Refund Amount"
        }
    )

    st.area_chart(
        distribution_df["Refund Amount"],
        x_label="Refund",
        y_label="Amount (USD)",
    )


# ============================================================
# TOP ORDERS
# ============================================================

st.subheader("🔝 Top 10 Orders by Refund")


top_orders_query = f"""
SELECT

    ORDER_ID,

    COUNT(DISTINCT ORDER_ITEM_ID)
        AS REFUND_ITEMS,

    SUM(REFUND_AMOUNT_USD)
        AS TOTAL_REFUND

FROM {FULL_TABLE_NAME}

{where_clause}

GROUP BY ORDER_ID

ORDER BY TOTAL_REFUND DESC

LIMIT 10
"""


top_orders_df = (
    session.sql(top_orders_query)
    .to_pandas()
)


if not top_orders_df.empty:

    top_orders_df["ORDER_ID"] = (
        top_orders_df["ORDER_ID"].astype(str)
    )

    top_orders_df = top_orders_df.set_index(
        "ORDER_ID"
    )

    st.bar_chart(
        top_orders_df["TOTAL_REFUND"],
        x_label="Order ID",
        y_label="Refund Amount (USD)",
    )


# ============================================================
# DETAILS
# ============================================================

st.subheader("📋 Refund Details")


details_query = f"""
SELECT

    ORDER_ITEM_REFUND_ID,
    CREATED_AT,
    ORDER_ITEM_ID,
    ORDER_ID,
    REFUND_AMOUNT_USD

FROM {FULL_TABLE_NAME}

{where_clause}

ORDER BY CREATED_AT DESC

LIMIT 1000
"""


details_df = (
    session.sql(details_query)
    .to_pandas()
)


st.dataframe(
    details_df,
    use_container_width=True,
    height=450,
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    f"Data Source: {FULL_TABLE_NAME}"
)