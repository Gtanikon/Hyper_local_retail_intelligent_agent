from mcp.server.fastmcp import FastMCP
import pandas as pd
from pathlib import Path
import hashlib
import json

mcp = FastMCP("Inventory Intelligence Safe MCP")

BASE_DIR = Path(r"C:\Users\gowth\Downloads\outputs")

SECRET_SALT = "change_this_secret_for_each_client_2026"


# -----------------------------
# Basic utilities
# -----------------------------

def load_csv(name: str) -> pd.DataFrame:
    path = BASE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path)


def tokenize(value, prefix: str) -> str:
    if pd.isna(value):
        return "UNKNOWN"
    raw = f"{SECRET_SALT}_{str(value)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()[:10]
    return f"{prefix}_{hashed}"


def classify_level(value, bins, labels):
    try:
        return pd.cut(
            pd.Series([value]),
            bins=bins,
            labels=labels,
            include_lowest=True
        ).iloc[0]
    except Exception:
        return "Unknown"


def safe_numeric_bins(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "total_stock" in df.columns:
        df["stock_level"] = pd.cut(
            df["total_stock"],
            bins=[-1, 10, 50, 150, float("inf")],
            labels=["Very Low", "Low", "Medium", "High"]
        )

    if "predicted_sales" in df.columns:
        df["demand_level"] = pd.cut(
            df["predicted_sales"],
            bins=[-1, 5, 20, 50, float("inf")],
            labels=["Low", "Medium", "High", "Very High"]
        )

    if "expected_stock" in df.columns:
        df["expected_stock_level"] = pd.cut(
            df["expected_stock"],
            bins=[-float("inf"), 0, 10, 50, 150, float("inf")],
            labels=["Negative/Zero", "Very Low", "Low", "Medium", "High"]
        )

    if "priority_score" in df.columns:
        df["priority_level"] = pd.cut(
            df["priority_score"],
            bins=[-1, 25, 50, 75, 100, float("inf")],
            labels=["Low", "Medium", "High", "Critical", "Extreme"]
        )

    return df


def remove_sensitive_columns(df: pd.DataFrame) -> pd.DataFrame:
    sensitive_cols = [
        "store_id",
        "sku_id",
        "transaction_id",
        "snapshot_id",
        "stockout_id",
        "forecast_id",
        "product_id",
        "supplier_id",
        "supplier_name",
        "replenishment_id",
        "promotion_id",
        "associate_id",
        "unit_price_actual",
        "revenue",
        "estimated_lost_revenue",
        "replenishment_cost",
        "city",
        "state",
        "address",
        "zip",
        "email",
        "phone"
    ]

    return df.drop(
        columns=[c for c in sensitive_cols if c in df.columns],
        errors="ignore"
    )


def build_safe_inventory_view() -> pd.DataFrame:
    df = load_csv("final_predictions_risks_actions.csv")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if "store_id" in df.columns:
        df["store_ref"] = df["store_id"].apply(lambda x: tokenize(x, "STORE"))

    if "sku_id" in df.columns:
        df["sku_ref"] = df["sku_id"].apply(lambda x: tokenize(x, "SKU"))

    df = safe_numeric_bins(df)
    df = remove_sensitive_columns(df)

    safe_cols = [
        "date",
        "region",
        "store_ref",
        "sku_ref",
        "stock_level",
        "demand_level",
        "expected_stock_level",
        "risk_category",
        "cause_label",
        "action",
        "stockout_risk",
        "phantom_flag_rule",
        "priority_level"
    ]

    safe_cols = [c for c in safe_cols if c in df.columns]
    return df[safe_cols].copy()


def build_safe_phantom_view() -> pd.DataFrame:
    df = load_csv("phantom_inventory_history.csv")

    if "store_id" in df.columns:
        df["store_ref"] = df["store_id"].apply(lambda x: tokenize(x, "STORE"))

    if "sku_id" in df.columns:
        df["sku_ref"] = df["sku_id"].apply(lambda x: tokenize(x, "SKU"))

    if "shelf_stock_gap" in df.columns:
        df["gap_level"] = pd.cut(
            df["shelf_stock_gap"],
            bins=[-float("inf"), 0, 10, 50, 100, float("inf")],
            labels=["No Gap", "Small", "Medium", "Large", "Very Large"]
        )

    if "expected_stock_at_snapshot" in df.columns:
        df["expected_stock_level"] = pd.cut(
            df["expected_stock_at_snapshot"],
            bins=[-float("inf"), 0, 10, 50, 150, float("inf")],
            labels=["Negative/Zero", "Very Low", "Low", "Medium", "High"]
        )

    if "units_on_hand" in df.columns:
        df["visible_stock_level"] = pd.cut(
            df["units_on_hand"],
            bins=[-1, 10, 50, 150, float("inf")],
            labels=["Very Low", "Low", "Medium", "High"]
        )

    df = remove_sensitive_columns(df)

    safe_cols = [
        "snapshot_date",
        "store_ref",
        "sku_ref",
        "expected_stock_level",
        "visible_stock_level",
        "gap_level",
        "phantom_flag"
    ]

    safe_cols = [c for c in safe_cols if c in df.columns]
    return df[safe_cols].copy()


def build_safe_transfer_view(file_name: str) -> pd.DataFrame:
    df = load_csv(file_name)

    for col in df.columns:
        lower = col.lower()

        if "store" in lower and df[col].dtype == "object":
            df[col + "_ref"] = df[col].apply(lambda x: tokenize(x, "STORE"))

        if "sku" in lower and df[col].dtype == "object":
            df[col + "_ref"] = df[col].apply(lambda x: tokenize(x, "SKU"))

    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols:
        if "unit" in col.lower() or "qty" in col.lower() or "stock" in col.lower():
            df[col + "_level"] = pd.cut(
                df[col],
                bins=[-1, 10, 50, 150, float("inf")],
                labels=["Very Low", "Low", "Medium", "High"]
            )

    df = remove_sensitive_columns(df)

    keep_cols = [
        c for c in df.columns
        if c.endswith("_ref")
        or c.endswith("_level")
        or c in ["region", "from_region", "to_region", "transfer_type", "priority_level"]
    ]

    if not keep_cols:
        keep_cols = df.columns[:8].tolist()

    return df[keep_cols].copy()


def table_registry():
    return {
        "inventory_risk_view": build_safe_inventory_view,
        "phantom_view": build_safe_phantom_view,
        "intra_transfer_view": lambda: build_safe_transfer_view("intra_region_transfers.csv"),
        "inter_transfer_view": lambda: build_safe_transfer_view("inter_region_transfers.csv"),
    }


def is_allowed_table(table_name: str) -> bool:
    return table_name in table_registry()


def safe_output(df: pd.DataFrame, limit: int = 20) -> str:
    if df.empty:
        return "No matching safe records found."

    limit = min(max(int(limit), 1), 50)
    return df.head(limit).to_string(index=False)


# -----------------------------
# MCP tools
# -----------------------------

@mcp.tool()
def list_safe_tables() -> str:
    """
    List the safe tables Claude is allowed to query.
    These tables hide raw client identifiers and sensitive numeric data.
    """
    return """
Available safe tables:

1. inventory_risk_view
   Purpose: latest inventory risks, stockout risk, phantom flags, actions, region-level analysis.

2. phantom_view
   Purpose: phantom inventory analysis using safe store/SKU references and gap levels.

3. intra_transfer_view
   Purpose: safe intra-region transfer recommendations.

4. inter_transfer_view
   Purpose: safe inter-region transfer recommendations.

Note:
Raw CSV tables are not exposed. Store IDs and SKU IDs are tokenized.
Exact sensitive values are converted into business levels.
"""


@mcp.tool()
def describe_safe_table(table_name: str) -> str:
    """
    Show safe columns available in a safe table.
    """
    if not is_allowed_table(table_name):
        return "Table not allowed. Use list_safe_tables() to see available safe tables."

    df = table_registry()[table_name]()
    return f"Safe table: {table_name}\nColumns:\n" + "\n".join(df.columns.tolist())


@mcp.tool()
def get_safe_sample(table_name: str, limit: int = 10) -> str:
    """
    Return a small safe sample from a safe table.
    """
    if not is_allowed_table(table_name):
        return "Table not allowed. Use list_safe_tables() to see available safe tables."

    df = table_registry()[table_name]()
    return safe_output(df, limit)


@mcp.tool()
def analyze_safe_table(
    table_name: str,
    group_by: str = "region",
    metric: str = "count",
    filter_column: str = "None",
    filter_value: str = "None",
    limit: int = 20
) -> str:
    """
    Generic safe analytics tool.

    Allowed metrics:
    - count
    - phantom_rate
    - stockout_rate

    Example:
    analyze_safe_table("inventory_risk_view", "region", "count")
    analyze_safe_table("inventory_risk_view", "risk_category", "count")
    analyze_safe_table("phantom_view", "gap_level", "phantom_rate")
    """
    if not is_allowed_table(table_name):
        return "Table not allowed. Use list_safe_tables() to see available safe tables."

    df = table_registry()[table_name]()

    if filter_column != "None" and filter_value != "None":
        if filter_column not in df.columns:
            return f"Filter column not available. Available columns: {list(df.columns)}"
        df = df[df[filter_column].astype(str) == str(filter_value)]

    if group_by not in df.columns:
        return f"Group-by column not available. Available columns: {list(df.columns)}"

    if metric == "count":
        result = (
            df.groupby(group_by)
            .size()
            .reset_index(name="record_count")
            .sort_values("record_count", ascending=False)
        )

    elif metric == "phantom_rate":
        if "phantom_flag" in df.columns:
            result = (
                df.groupby(group_by)["phantom_flag"]
                .mean()
                .reset_index(name="phantom_rate")
                .sort_values("phantom_rate", ascending=False)
            )
        elif "phantom_flag_rule" in df.columns:
            result = (
                df.groupby(group_by)["phantom_flag_rule"]
                .mean()
                .reset_index(name="phantom_rate")
                .sort_values("phantom_rate", ascending=False)
            )
        else:
            return "phantom_rate is not available for this table."

    elif metric == "stockout_rate":
        if "stockout_risk" not in df.columns:
            return "stockout_rate is not available for this table."

        result = (
            df.groupby(group_by)["stockout_risk"]
            .mean()
            .reset_index(name="stockout_rate")
            .sort_values("stockout_rate", ascending=False)
        )

    else:
        return "Metric not allowed. Use count, phantom_rate, or stockout_rate."

    return safe_output(result, limit)


@mcp.tool()
def get_safe_manager_action_plan(region: str = "All", limit: int = 10) -> str:
    """
    Generate a safe manager action plan without exposing raw store IDs, SKU IDs, or exact numbers.
    """
    df = build_safe_inventory_view()

    if "date" in df.columns:
        latest_date = df["date"].max()
        df = df[df["date"] == latest_date]
    else:
        latest_date = "Unknown"

    if region != "All" and "region" in df.columns:
        df = df[df["region"] == region]

    risky = df.copy()

    if "risk_category" in risky.columns:
        risky = risky[risky["risk_category"].astype(str) != "Normal"]

    if "priority_level" in risky.columns:
        priority_order = {
            "Extreme": 5,
            "Critical": 4,
            "High": 3,
            "Medium": 2,
            "Low": 1
        }
        risky["priority_rank"] = risky["priority_level"].astype(str).map(priority_order).fillna(0)
        risky = risky.sort_values("priority_rank", ascending=False)

    issue_summary = (
        risky.groupby(["region", "risk_category", "cause_label", "action"])
        .size()
        .reset_index(name="issue_count")
        .sort_values("issue_count", ascending=False)
        if all(c in risky.columns for c in ["region", "risk_category", "cause_label", "action"])
        else risky.head(limit)
    )

    return f"""
SAFE DAILY MANAGER ACTION PLAN

Latest operational date: {latest_date}
Region filter: {region}

1. Main issue summary:
{safe_output(issue_summary, limit)}

2. Recommended sequence:
- Start with Critical/High priority issues.
- Handle stockout risks first.
- Check phantom inventory cases through shelf and backroom audit.
- Use intra-region transfers before inter-region transfers.
- Adjust shelf space for repeated overstock/understock patterns.

Privacy protection:
- Raw store IDs are hidden.
- Raw SKU IDs are hidden.
- Exact sensitive numeric values are converted into levels.
- Claude only receives safe operational summaries.
"""


@mcp.tool()
def privacy_policy_summary() -> str:
    """
    Explain what data protection is applied in this MCP server.
    """
    return """
This MCP server uses a privacy layer before returning data to Claude.

Protections applied:
1. Store IDs are tokenized.
2. SKU IDs are tokenized.
3. Transaction IDs, snapshot IDs, replenishment IDs, promotion IDs, and associate IDs are removed.
4. Revenue, unit price, supplier details, and exact sensitive operational values are removed.
5. Exact stock and demand numbers are converted into levels.
6. Claude can query only approved safe views.
7. Raw CSV tables are never directly exposed through MCP tools.
"""


if __name__ == "__main__":
    mcp.run()