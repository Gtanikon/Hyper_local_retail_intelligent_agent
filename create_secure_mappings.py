import pandas as pd
import hashlib
from pathlib import Path

BASE_DIR = Path(r"C:\Users\gowth\Downloads\outputs")
INPUT_FILE = BASE_DIR / "final_predictions_risks_actions.csv"

SECRET_SALT = "change_this_secret_for_each_client_2026"

df = pd.read_csv(INPUT_FILE)

def tokenize(value, prefix):
    raw = f"{SECRET_SALT}_{str(value)}"
    return f"{prefix}_{hashlib.sha256(raw.encode()).hexdigest()[:10]}"

store_map = (
    df[["store_id"]]
    .drop_duplicates()
    .assign(store_ref=lambda x: x["store_id"].apply(lambda v: tokenize(v, "STORE")))
)

sku_map = (
    df[["sku_id"]]
    .drop_duplicates()
    .assign(sku_ref=lambda x: x["sku_id"].apply(lambda v: tokenize(v, "SKU")))
)

store_map.to_csv(BASE_DIR / "secure_store_mapping.csv", index=False)
sku_map.to_csv(BASE_DIR / "secure_sku_mapping.csv", index=False)

print("Created:")
print(BASE_DIR / "secure_store_mapping.csv")
print(BASE_DIR / "secure_sku_mapping.csv")