import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText

# -------------------------
# Page Setup
# -------------------------
st.set_page_config(
    page_title="Inventory Intelligence Dashboard",
    layout="wide"
)

st.title("📦 Inventory Intelligence & Alerting Dashboard")

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    final_predictions_df = pd.read_csv("outputs/final_predictions_risks_actions.csv")
    phantom = pd.read_csv("outputs/phantom_inventory_history.csv")
    shelf = pd.read_csv("outputs/store_shelf_space_reallocation.csv")
    intra = pd.read_csv("outputs/intra_region_transfers.csv")
    inter = pd.read_csv("outputs/inter_region_transfers.csv")
    product_region = pd.read_csv("outputs/product_region_table.csv")
    model_comp = pd.read_csv("outputs/model_comparison.csv")

    final_predictions_df["date"] = pd.to_datetime(final_predictions_df["date"], errors="coerce")

    if "snapshot_date" in phantom.columns:
        phantom["snapshot_date"] = pd.to_datetime(phantom["snapshot_date"], errors="coerce")

    return final_predictions_df, phantom, shelf, intra, inter, product_region, model_comp


df, phantom, shelf, intra, inter, product_region, model_comp = load_data()

latest_date = df["date"].max()
latest_df = df[df["date"] == latest_date].copy()

# -------------------------
# Sidebar Global Filters
# -------------------------
st.sidebar.header("🔎 Global Filters")

date_options = sorted(df["date"].dropna().dt.date.unique())

selected_date = st.sidebar.selectbox(
    "Operational Date",
    date_options,
    index=len(date_options) - 1
)

selected_region = st.sidebar.selectbox(
    "Region",
    ["All"] + sorted(df["region"].dropna().unique().tolist()) if "region" in df.columns else ["All"]
)

selected_store = st.sidebar.selectbox(
    "Store",
    ["All"] + sorted(df["store_id"].dropna().unique().tolist()) if "store_id" in df.columns else ["All"]
)

selected_sku = st.sidebar.selectbox(
    "SKU",
    ["All"] + sorted(df["sku_id"].dropna().unique().tolist()) if "sku_id" in df.columns else ["All"]
)

# -------------------------
# Filter Helpers
# -------------------------
def apply_common_filters(data, date_filter=False):
    temp = data.copy()

    if date_filter and "date" in temp.columns:
        temp = temp[temp["date"].dt.date == selected_date]

    if selected_region != "All" and "region" in temp.columns:
        temp = temp[temp["region"] == selected_region]

    if selected_store != "All" and "store_id" in temp.columns:
        temp = temp[temp["store_id"] == selected_store]

    if selected_sku != "All" and "sku_id" in temp.columns:
        temp = temp[temp["sku_id"] == selected_sku]

    return temp


filtered_df = apply_common_filters(df, date_filter=True)
historical_filtered_df = apply_common_filters(df, date_filter=False)

# Phantom filter
phantom_filtered = phantom.copy()
if selected_store != "All" and "store_id" in phantom_filtered.columns:
    phantom_filtered = phantom_filtered[phantom_filtered["store_id"] == selected_store]
if selected_sku != "All" and "sku_id" in phantom_filtered.columns:
    phantom_filtered = phantom_filtered[phantom_filtered["sku_id"] == selected_sku]

# Shelf filter
shelf_filtered = shelf.copy()
if selected_region != "All" and "region" in shelf_filtered.columns:
    shelf_filtered = shelf_filtered[shelf_filtered["region"] == selected_region]
if selected_store != "All" and "store_id" in shelf_filtered.columns:
    shelf_filtered = shelf_filtered[shelf_filtered["store_id"] == selected_store]

# Transfer filters
intra_filtered = intra.copy()
inter_filtered = inter.copy()

if selected_sku != "All":
    if "sku_id" in intra_filtered.columns:
        intra_filtered = intra_filtered[intra_filtered["sku_id"] == selected_sku]
    if "sku_id" in inter_filtered.columns:
        inter_filtered = inter_filtered[inter_filtered["sku_id"] == selected_sku]

if selected_region != "All":
    possible_intra_region_cols = [
        "region", "donor_region", "receiver_region", "region_donor", "region_receiver"
    ]

    intra_region_cols = [c for c in possible_intra_region_cols if c in intra_filtered.columns]
    if intra_region_cols:
        mask = False
        for c in intra_region_cols:
            mask = mask | (intra_filtered[c] == selected_region)
        intra_filtered = intra_filtered[mask]

    inter_region_cols = [c for c in ["region_donor", "region_receiver", "donor_region", "receiver_region"] if c in inter_filtered.columns]
    if inter_region_cols:
        mask = False
        for c in inter_region_cols:
            mask = mask | (inter_filtered[c] == selected_region)
        inter_filtered = inter_filtered[mask]

# Product-region filter
product_region_filtered = product_region.copy()
if selected_sku != "All" and "sku_id" in product_region_filtered.columns:
    product_region_filtered = product_region_filtered[product_region_filtered["sku_id"] == selected_sku]

# -------------------------
# Tabs
# -------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Executive Overview",
    "Phantom Inventory",
    "Forecasting",
    "Risk & Cause Labels",
    "Shelf Optimization",
    "Transfers",
    "Latest Manager View",
    "Email Alerts"
])

# -------------------------
# TAB 1: Executive Overview
# -------------------------
with tab1:
    st.header("Executive Overview")

    issue_df = filtered_df[
        (filtered_df["risk_category"] != "Normal") |
        (filtered_df["stockout_risk"] == 1) |
        (filtered_df["phantom_flag_rule"] == 1)
    ].copy() if len(filtered_df) > 0 else pd.DataFrame()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Selected Date", str(selected_date))
    col2.metric("Filtered Risk Cases", len(issue_df))
    col3.metric("Intra-region Transfers", len(intra_filtered))
    col4.metric("Inter-region Transfers", len(inter_filtered))

    st.subheader("Filtered Risk Category Distribution")
    if len(filtered_df) > 0 and "risk_category" in filtered_df.columns:
        st.bar_chart(filtered_df["risk_category"].value_counts())
    else:
        st.warning("No records found for the selected filters.")

    if len(filtered_df) > 0 and "action" in filtered_df.columns:
        st.subheader("Filtered Action Distribution")
        st.bar_chart(filtered_df["action"].value_counts())

    st.subheader("Filtered Operational Records")
    st.dataframe(filtered_df.head(300), use_container_width=True)

# -------------------------
# TAB 2: Phantom Inventory
# -------------------------
with tab2:
    st.header("Phantom Inventory Detection")

    total_cases = len(phantom_filtered)
    phantom_cases = int(phantom_filtered["phantom_flag"].sum()) if "phantom_flag" in phantom_filtered.columns else 0
    phantom_rate = phantom_cases / total_cases if total_cases > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Movement Records", f"{total_cases:,}")
    col2.metric("Phantom Cases", f"{phantom_cases:,}")
    col3.metric("Phantom Rate", f"{phantom_rate:.2%}")

    if len(phantom_filtered) > 0 and "phantom_flag" in phantom_filtered.columns:
        st.subheader("Phantom vs Non-Phantom")
        phantom_counts = phantom_filtered["phantom_flag"].value_counts().sort_index()
        phantom_counts.index = ["Non-Phantom" if i == 0 else "Phantom" for i in phantom_counts.index]
        st.bar_chart(phantom_counts)

    st.subheader("Phantom Records")
    phantom_cols = [
        "store_id", "sku_id", "snapshot_date",
        "expected_stock_at_snapshot",
        "units_on_hand",
        "shelf_stock_gap",
        "phantom_flag"
    ]
    phantom_cols = [c for c in phantom_cols if c in phantom_filtered.columns]

    if len(phantom_filtered) > 0:
        if "shelf_stock_gap" in phantom_filtered.columns:
            st.dataframe(
                phantom_filtered[phantom_cols]
                .sort_values("shelf_stock_gap", ascending=False)
                .head(300),
                use_container_width=True
            )
        else:
            st.dataframe(phantom_filtered[phantom_cols].head(300), use_container_width=True)
    else:
        st.info("No phantom records for the selected filters.")

# -------------------------
# TAB 3: Forecasting
# -------------------------
with tab3:
    st.header("Forecasting Model Performance")

    st.subheader("Model Comparison")
    st.dataframe(model_comp, use_container_width=True)

    if "Model" in model_comp.columns and "RMSE" in model_comp.columns:
        st.subheader("RMSE Comparison")
        st.bar_chart(model_comp.set_index("Model")["RMSE"])

    st.subheader("Actual vs Predicted Sales Over Time")

    if len(historical_filtered_df) > 0:
        forecast_trend = (
            historical_filtered_df.groupby("date", as_index=False)
            .agg(
                actual_sales=("daily_units_sold", "sum"),
                predicted_sales=("predicted_sales", "sum")
            )
        )

        st.line_chart(
            forecast_trend.set_index("date")[["actual_sales", "predicted_sales"]]
        )

        st.subheader("Forecast Detail Table")
        forecast_cols = [
            "store_id", "sku_id", "region", "date",
            "daily_units_sold", "predicted_sales",
            "target_next_day_sales"
        ]
        forecast_cols = [c for c in forecast_cols if c in historical_filtered_df.columns]
        st.dataframe(historical_filtered_df[forecast_cols].head(300), use_container_width=True)
    else:
        st.warning("No forecast data for the selected filters.")

# -------------------------
# TAB 4: Risk & Cause Labels
# -------------------------
with tab4:
    st.header("Risk & Cause Labels")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Risk Category Distribution")
        if len(historical_filtered_df) > 0 and "risk_category" in historical_filtered_df.columns:
            st.bar_chart(historical_filtered_df["risk_category"].value_counts())

    with col2:
        st.subheader("Cause Label Distribution")
        if len(historical_filtered_df) > 0 and "cause_label" in historical_filtered_df.columns:
            st.bar_chart(historical_filtered_df["cause_label"].value_counts())

    st.subheader("Risk + Cause + Action Table")

    risk_cols = [
        "store_id", "sku_id", "region", "city", "state", "date",
        "total_stock", "predicted_sales", "expected_stock",
        "stockout_risk", "phantom_flag_rule",
        "risk_category", "cause_label",
        "action", "priority_score"
    ]
    risk_cols = [c for c in risk_cols if c in historical_filtered_df.columns]

    risk_table = historical_filtered_df.copy()
    if "priority_score" in risk_table.columns:
        risk_table = risk_table.sort_values("priority_score", ascending=False)

    st.dataframe(risk_table[risk_cols].head(500), use_container_width=True)

# -------------------------
# TAB 5: Shelf Optimization
# -------------------------
with tab5:
    st.header("Shelf Optimization")

    col1, col2, col3 = st.columns(3)

    col1.metric("Stores with Shelf Recommendations", len(shelf_filtered))
    col2.metric(
        "Overstocked Product Count",
        int(shelf_filtered["overstocked_product_count"].sum()) if "overstocked_product_count" in shelf_filtered.columns else 0
    )
    col3.metric(
        "Understocked Product Count",
        int(shelf_filtered["understocked_product_count"].sum()) if "understocked_product_count" in shelf_filtered.columns else 0
    )

    shelf_cols = [
        "store_id", "region",
        "overstocked_product_count",
        "understocked_product_count",
        "total_excess_units",
        "total_needed_units",
        "products_to_reduce_space",
        "products_to_increase_space",
        "shelf_space_recommendation"
    ]
    shelf_cols = [c for c in shelf_cols if c in shelf_filtered.columns]

    st.subheader("Shelf Space Reallocation Table")
    st.dataframe(shelf_filtered[shelf_cols].head(500), use_container_width=True)

    if len(shelf_filtered) > 0 and "total_needed_units" in shelf_filtered.columns:
        st.subheader("Top Stores by Needed Units")
        top_needed = shelf_filtered.sort_values("total_needed_units", ascending=False).head(20)
        st.bar_chart(top_needed.set_index("store_id")["total_needed_units"])

# -------------------------
# TAB 6: Transfers
# -------------------------
with tab6:
    st.header("Transfer Recommendations")

    col1, col2 = st.columns(2)
    col1.metric("Intra-region Transfers", len(intra_filtered))
    col2.metric("Inter-region Transfers", len(inter_filtered))

    st.subheader("Intra-region Store-to-Store Transfers")
    st.dataframe(intra_filtered.head(500), use_container_width=True)

    st.subheader("Inter-region Product Transfers")
    st.dataframe(inter_filtered.head(500), use_container_width=True)

    if len(inter_filtered) > 0 and "region_donor" in inter_filtered.columns and "transfer_qty" in inter_filtered.columns:
        st.subheader("Transfer Quantity by Donor Region")
        st.bar_chart(inter_filtered.groupby("region_donor")["transfer_qty"].sum())

    if len(inter_filtered) > 0 and "region_receiver" in inter_filtered.columns and "transfer_qty" in inter_filtered.columns:
        st.subheader("Transfer Quantity by Receiver Region")
        st.bar_chart(inter_filtered.groupby("region_receiver")["transfer_qty"].sum())

# -------------------------
# TAB 7: Latest Manager View
# -------------------------
with tab7:
    st.header("Latest Manager Drill-Down View")

    st.write(f"Selected operational date: **{selected_date}**")

    issue_df = filtered_df[
        (filtered_df["risk_category"] != "Normal") |
        (filtered_df["stockout_risk"] == 1) |
        (filtered_df["phantom_flag_rule"] == 1)
    ].copy() if len(filtered_df) > 0 else pd.DataFrame()

    if "priority_score" in issue_df.columns:
        issue_df = issue_df.sort_values("priority_score", ascending=False)

    col1, col2, col3 = st.columns(3)
    col1.metric("Issues in Selection", len(issue_df))
    col2.metric("Stockout Risk", int(filtered_df["stockout_risk"].sum()) if "stockout_risk" in filtered_df.columns and len(filtered_df) > 0 else 0)
    col3.metric("Phantom Flags", int(filtered_df["phantom_flag_rule"].sum()) if "phantom_flag_rule" in filtered_df.columns and len(filtered_df) > 0 else 0)

    st.subheader("Manager Issue Table")
    manager_cols = [
        "store_id", "sku_id", "product_name", "region", "city", "state", "date",
        "total_stock", "predicted_sales", "expected_stock",
        "stockout_risk", "phantom_flag_rule",
        "risk_category", "cause_label",
        "action", "priority_score"
    ]
    manager_cols = [c for c in manager_cols if c in issue_df.columns]

    st.dataframe(issue_df[manager_cols].head(500), use_container_width=True)

    if selected_store != "All":
        st.subheader(f"Store Drill-Down: {selected_store}")

        store_shelf = shelf[shelf["store_id"] == selected_store] if "store_id" in shelf.columns else pd.DataFrame()
        st.write("Shelf Recommendations for Selected Store")
        st.dataframe(store_shelf.head(100), use_container_width=True)

        if "store_id" in intra.columns:
            store_intra = intra[intra["store_id"] == selected_store]
            st.write("Intra-region Transfers for Selected Store")
            st.dataframe(store_intra.head(100), use_container_width=True)

    if selected_sku != "All":
        st.subheader(f"SKU Drill-Down: {selected_sku}")

        sku_trend = (
            df[df["sku_id"] == selected_sku]
            .groupby("date", as_index=False)
            .agg(
                actual_sales=("daily_units_sold", "sum"),
                predicted_sales=("predicted_sales", "sum")
            )
        )

        st.line_chart(sku_trend.set_index("date")[["actual_sales", "predicted_sales"]])

    st.subheader("Product-Region Planning Table")
    st.dataframe(product_region_filtered.head(300), use_container_width=True)

# -------------------------
# TAB 8: Email Alerts
# -------------------------
def send_email_alert(sender, app_password, receiver, subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, app_password)
        server.send_message(msg)


with tab8:
    st.header("Email Alerts")

    issue_df = filtered_df[
        (filtered_df["risk_category"] != "Normal") |
        (filtered_df["stockout_risk"] == 1) |
        (filtered_df["phantom_flag_rule"] == 1)
    ].copy() if len(filtered_df) > 0 else pd.DataFrame()

    latest_issue_count = len(issue_df)

    if "priority_score" in issue_df.columns and len(issue_df) > 0:
        high_priority_count = len(
            issue_df[issue_df["priority_score"] >= issue_df["priority_score"].quantile(0.90)]
        )
    else:
        high_priority_count = latest_issue_count

    col1, col2, col3 = st.columns(3)
    col1.metric("Issue Count", latest_issue_count)
    col2.metric("High Priority Alerts", high_priority_count)
    col3.metric("Transfers Suggested", len(intra_filtered) + len(inter_filtered))

    sender = st.text_input("Sender Gmail")
    receiver = st.text_input("Receiver Email")
    app_password = st.text_input("Gmail App Password", type="password")

    alert_message = f"""
Inventory Alert - Operational Issues

Date: {selected_date}
Region: {selected_region}
Store: {selected_store}
SKU: {selected_sku}

Issue count: {latest_issue_count}
High priority alerts: {high_priority_count}
Intra-region transfers suggested: {len(intra_filtered)}
Inter-region transfers suggested: {len(inter_filtered)}
Shelf optimization stores: {len(shelf_filtered)}

Recommended actions:
1. Review the Manager Drill-Down View.
2. Prioritize high-risk stockout and phantom cases.
3. Execute feasible intra-region transfers first.
4. Use inter-region transfers when local transfer is not enough.
5. Reallocate shelf space based on overstock and understock recommendations.
"""

    st.text_area("Email Preview", alert_message, height=260)

    if st.button("Send Alert Email"):
        send_email_alert(
            sender,
            app_password,
            receiver,
            "Inventory Alert - Operational Issues",
            alert_message
        )
        st.success("Alert email sent successfully.")