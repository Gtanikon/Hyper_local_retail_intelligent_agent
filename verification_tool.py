import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# CONFIG
# =========================

BASE_DIR = Path(r"C:\Users\gowth\Downloads\outputs")

STORE_MAPPING_FILE = BASE_DIR / "secure_store_mapping.csv"
SKU_MAPPING_FILE = BASE_DIR / "secure_sku_mapping.csv"

st.set_page_config(
    page_title="Secure Verification Tool",
    page_icon="🔐",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_mapping(file_path):
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_csv(file_path)

store_map = load_mapping(STORE_MAPPING_FILE)
sku_map = load_mapping(SKU_MAPPING_FILE)

# =========================
# BASIC PASSWORD GATE
# =========================

st.sidebar.title("🔐 Access Control")

password = st.sidebar.text_input("Enter verification password", type="password")

ADMIN_PASSWORD = "client_verify_2026"   # change this before sharing

if password != ADMIN_PASSWORD:
    st.warning("Enter the verification password to access this tool.")
    st.stop()

# =========================
# HEADER
# =========================

st.title("🔐 Secure Store & SKU Verification Tool")

st.markdown("""
This tool allows authorized users to map anonymized Claude/MCP references back to real internal IDs.

Claude sees only safe IDs like:

- `STORE_0fc2f91089`
- `SKU_7d21ab34`

This tool verifies them internally.
""")

# =========================
# TABS
# =========================

tab1, tab2, tab3 = st.tabs([
    "🏬 Verify Store",
    "📦 Verify SKU",
    "📋 Bulk Verification"
])

# =========================
# TAB 1: STORE VERIFY
# =========================

with tab1:
    st.subheader("🏬 Verify Store Reference")

    if store_map.empty:
        st.error(f"Store mapping file not found: {STORE_MAPPING_FILE}")
    else:
        st.write("Enter the `STORE_REF` shown by Claude.")

        store_ref = st.text_input(
            "Store Reference",
            placeholder="Example: STORE_0fc2f91089"
        )

        if st.button("Verify Store"):
            if not store_ref:
                st.warning("Please enter a store reference.")
            else:
                result = store_map[
                    store_map["store_ref"].astype(str).str.strip()
                    == store_ref.strip()
                ]

                if result.empty:
                    st.error("No matching store found.")
                else:
                    st.success("Store verified successfully.")

                    st.dataframe(
                        result,
                        use_container_width=True,
                        hide_index=True
                    )

# =========================
# TAB 2: SKU VERIFY
# =========================

with tab2:
    st.subheader("📦 Verify SKU Reference")

    if sku_map.empty:
        st.error(f"SKU mapping file not found: {SKU_MAPPING_FILE}")
    else:
        st.write("Enter the `SKU_REF` shown by Claude.")

        sku_ref = st.text_input(
            "SKU Reference",
            placeholder="Example: SKU_7d21ab34"
        )

        if st.button("Verify SKU"):
            if not sku_ref:
                st.warning("Please enter a SKU reference.")
            else:
                result = sku_map[
                    sku_map["sku_ref"].astype(str).str.strip()
                    == sku_ref.strip()
                ]

                if result.empty:
                    st.error("No matching SKU found.")
                else:
                    st.success("SKU verified successfully.")

                    st.dataframe(
                        result,
                        use_container_width=True,
                        hide_index=True
                    )

# =========================
# TAB 3: BULK VERIFY
# =========================

with tab3:
    st.subheader("📋 Bulk Verification")

    st.markdown("""
Paste multiple references below, one per line.

Example:

```text
STORE_0fc2f91089
STORE_10931a7b99
SKU_7d21ab34
SKU_91ab22ef
""")

refs_text = st.text_area("Paste STORE_REF or SKU_REF values here")

if st.button("Run Bulk Verification"):
    if not refs_text.strip():
        st.warning("Please paste at least one reference.")
    else:
        refs = [
            r.strip()
            for r in refs_text.splitlines()
            if r.strip()
        ]

        store_results = []
        sku_results = []
        missing = []

        for ref in refs:
            if ref.startswith("STORE_"):
                match = store_map[
                    store_map["store_ref"].astype(str).str.strip()
                    == ref
                ]

                if not match.empty:
                    store_results.append(match)
                else:
                    missing.append(ref)

            elif ref.startswith("SKU_"):
                match = sku_map[
                    sku_map["sku_ref"].astype(str).str.strip()
                    == ref
                ]

                if not match.empty:
                    sku_results.append(match)
                else:
                    missing.append(ref)

            else:
                missing.append(ref)

        if store_results:
            st.success("Verified store references")
            st.dataframe(
                pd.concat(store_results),
                use_container_width=True,
                hide_index=True
            )

        if sku_results:
            st.success("Verified SKU references")
            st.dataframe(
                pd.concat(sku_results),
                use_container_width=True,
                hide_index=True
            )

        if missing:
            st.error("References not found")
            st.write(missing)