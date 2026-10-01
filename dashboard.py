
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from pymongo import MongoClient
from dotenv import load_dotenv

# ---------------- CONFIGURATION ----------------
st.set_page_config(
    page_title="E-commerce Sales Analytics",
    page_icon="📊",
    layout="wide"
)

load_dotenv(r"D:\SDA-10\.env")
MONGO_URI = os.getenv("MONGO_URI")

DB_NAME = "ecommerce_analytics"
COLLECTION = "orders"

# ---------------- DASHBOARD HEADER ----------------
st.title("📊 Real-Time E-commerce Sales Analytics")
st.caption(
    "Kafka → Python Consumer → MongoDB Atlas → Streamlit | "
    "Inventory Replenishment Decision Support"
)

if not MONGO_URI:
    st.error("MongoDB URI not found. Check your .env file.")
    st.stop()

# ---------------- DATA LOADING ----------------
@st.cache_resource
def get_collection():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000)
    client.admin.command("ping")
    return client[DB_NAME][COLLECTION]

try:
    collection = get_collection()
except Exception as e:
    st.error(f"MongoDB connection failed: {e}")
    st.stop()


@st.fragment(run_every="5s")
def live_dashboard():
    documents = list(collection.find({}, {"_id": 0}))

    if not documents:
        st.warning("No orders found. Start your Kafka producer.")
        return

    df = pd.DataFrame(documents)

    required = [
        "order_id", "product", "category", "quantity",
        "price", "total_amount", "payment_method"
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        st.error(f"Missing required fields: {missing}")
        return

    for col in ["quantity", "price", "total_amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["product"] = df["product"].fillna("Unknown")
    df["category"] = df["category"].fillna("Unknown")
    df["payment_method"] = df["payment_method"].fillna("Unknown")

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"], errors="coerce", utc=True
        )
    else:
        df["timestamp"] = pd.NaT

    df = df.drop_duplicates(subset=["order_id"], keep="last")

    total_orders = len(df)
    revenue = df["total_amount"].sum()
    units_sold = df["quantity"].sum()
    avg_order = revenue / total_orders if total_orders else 0

    # ---------------- LIVE KPIs ----------------
    st.subheader("Live Business Overview")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Orders", f"{total_orders:,}")
    k2.metric("Total Revenue", f"₹{revenue:,.2f}")
    k3.metric("Units Sold", f"{units_sold:,.0f}")
    k4.metric("Average Order Value", f"₹{avg_order:,.2f}")

    st.caption(
        "Dashboard refreshes every 5 seconds. "
        "Metrics reflect orders currently stored in MongoDB."
    )

    # ---------------- TIME ANALYSIS ----------------
    st.divider()
    st.subheader("Sales Performance Over Time")

    timed = df.dropna(subset=["timestamp"]).copy()

    if not timed.empty:
        timed["time_bucket"] = timed["timestamp"].dt.floor("5min")
        trend = (
            timed.groupby("time_bucket", as_index=False)
            .agg(
                Revenue=("total_amount", "sum"),
                Orders=("order_id", "nunique")
            )
            .sort_values("time_bucket")
        )

        fig = px.line(
            trend,
            x="time_bucket",
            y="Revenue",
            markers=True,
            title="Revenue Trend (5-Minute Intervals)",
            labels={"time_bucket": "Time", "Revenue": "Revenue (₹)"}
        )
        st.plotly_chart(fig, use_container_width=True)

        fig_orders = px.line(
            trend,
            x="time_bucket",
            y="Orders",
            markers=True,
            title="Order Volume Over Time",
            labels={"time_bucket": "Time", "Orders": "Orders"}
        )
        st.plotly_chart(fig_orders, use_container_width=True)
    else:
        st.info("Valid timestamps are needed to display time trends.")

    # ---------------- CATEGORY ANALYSIS ----------------
    st.divider()
    st.subheader("Category-Wise Performance")

    category_data = (
        df.groupby("category", as_index=False)
        .agg(
            Revenue=("total_amount", "sum"),
            Units=("quantity", "sum"),
            Orders=("order_id", "nunique")
        )
        .sort_values("Revenue", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            category_data,
            x="category",
            y="Revenue",
            title="Revenue by Category",
            color="category",
            labels={"category": "Category", "Revenue": "Revenue (₹)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            df,
            names="payment_method",
            values="total_amount",
            title="Revenue by Payment Method",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- TOP PRODUCTS ----------------
    st.divider()
    st.subheader("Product Performance")

    product_data = (
        df.groupby("product", as_index=False)
        .agg(
            Revenue=("total_amount", "sum"),
            Units_Sold=("quantity", "sum"),
            Orders=("order_id", "nunique")
        )
        .sort_values("Units_Sold", ascending=False)
    )

    top_products = product_data.head(10)

    fig = px.bar(
        top_products.sort_values("Units_Sold"),
        x="Units_Sold",
        y="product",
        orientation="h",
        title="Top 10 Products by Units Sold",
        labels={"Units_Sold": "Units Sold", "product": "Product"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------------- INVENTORY DECISION SUPPORT ----------------
    st.divider()
    st.subheader("📦 Inventory Replenishment Decision Support")

    st.caption(
        "Illustrative stock estimates only. Actual inventory data "
        "is not currently connected. The assumed stock values are "
        "for demonstrating the replenishment use case."
    )

    # Stable simulated starting inventory per product
    def assumed_stock(product):
        seed = sum(ord(ch) for ch in str(product))
        return 20 + (seed % 61)

    inventory = product_data.copy()
    inventory["Assumed_Stock"] = inventory["product"].apply(assumed_stock)

    inventory["Estimated_Remaining"] = (
        inventory["Assumed_Stock"] - inventory["Units_Sold"]
    ).clip(lower=0)

    inventory["Stock_Coverage"] = (
        inventory["Estimated_Remaining"] /
        inventory["Units_Sold"].replace(0, float("nan"))
    )

    inventory["Status"] = inventory.apply(
        lambda row:
            "Replenishment Review"
            if row["Estimated_Remaining"] <= 10
            else "Monitor"
            if row["Units_Sold"] >= 10
            else "Normal",
        axis=1
    )

    inventory = inventory.sort_values(
        ["Estimated_Remaining", "Units_Sold"],
        ascending=[True, False]
    )

    alerts = inventory[
        inventory["Status"] == "Replenishment Review"
    ]

    a1, a2 = st.columns(2)
    a1.metric("Products to Review", len(alerts))
    a2.metric("Products Monitored", len(inventory))

    st.dataframe(
        inventory[
            [
                "product", "Units_Sold", "Assumed_Stock",
                "Estimated_Remaining", "Status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    if not alerts.empty:
        st.warning(
            "Some products have reached the illustrative "
            "replenishment threshold. Review their stock before "
            "placing a replenishment order."
        )
    else:
        st.success(
            "No products currently meet the illustrative "
            "replenishment review threshold."
        )

    # ---------------- BUSINESS INSIGHTS ----------------
    st.divider()
    st.subheader("Business Insights")

    if not category_data.empty:
        top_category = category_data.iloc[0]
        st.write(
            f"- **Leading revenue category:** "
            f"{top_category['category']} generated "
            f"₹{top_category['Revenue']:,.2f}."
        )

    if not product_data.empty:
        best_product = product_data.iloc[0]
        st.write(
            f"- **Highest unit sales:** {best_product['product']} "
            f"with {best_product['Units_Sold']:.0f} units sold."
        )

    if not alerts.empty:
        alert_products = ", ".join(
            alerts["product"].astype(str).head(5).tolist()
        )
        st.write(
            f"- **Inventory action:** Review stock for "
            f"{alert_products}. These products meet the "
            f"simulated low-stock threshold."
        )

    st.caption(
        "Insights are descriptive of the stored dataset. "
        "Replenishment signals are based on simulated stock "
        "assumptions, not actual warehouse inventory."
    )

    # ---------------- RAW DATA ----------------
    with st.expander("View Consumed Order Data"):
        st.dataframe(df, use_container_width=True, hide_index=True)


live_dashboard()