
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "orders_sample.csv"
OUTPUT_DIR = BASE_DIR / "analysis"
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_FILE)


duplicate_rows = df[df.duplicated("order_id", keep=False)].sort_values("order_id")

conflicting_ids = [
    order_id
    for order_id, group in duplicate_rows.groupby("order_id")
    if len(group.drop_duplicates()) > 1
]

# print("\nDUPLICATE ID VALIDATION")
# print("Rows with repeated order IDs:", len(duplicate_rows))
# print("Distinct IDs with repetitions:", duplicate_rows["order_id"].nunique())
# print("IDs with conflicting records:", len(conflicting_ids))
# print("Examples of conflicting IDs:", conflicting_ids[:10])

# print(df["payment_method"].value_counts(dropna=False).to_string())

print("ORIGINAL DATASET")
print("Total rows:", len(df))
print("Total columns:", len(df.columns))
print("Duplicate order IDs:", df["order_id"].duplicated().sum())
print("Exact duplicate rows:", df.duplicated().sum())
print("\nMissing values:")
print(df.isna().sum().to_string())

df = df.drop_duplicates().copy()

df["final_status"] = (
    df["final_status"]
    .astype("string")
    .str.strip()
    .str.upper()
)

df["order_datetime"] = pd.to_datetime(
    df["order_datetime"], errors="coerce"
)

df["address"] = df["address"].fillna("").astype(str).str.strip()

df["city"] = df["city"].fillna("Unknown").astype(str).str.strip()
df.loc[df["city"] == "", "city"] = "Unknown"


df["pincode"] = df["pincode"].astype("string").str.replace(
    r"\.0$", "", regex=True
)

df["address_length"] = df["address"].str.len()

known = df[df["final_status"].isin(["DELIVERED", "RTO"])].copy()
known["is_rto"] = (known["final_status"] == "RTO").astype(int)

print("\nCLEANED DATASET")
print("Rows after removing exact duplicates:", len(df))
print("Known delivery outcomes:", len(known))
print("Delivered:", (known["is_rto"] == 0).sum())
print("RTO:", known["is_rto"].sum())
print("Overall RTO rate:", round(known["is_rto"].mean() * 100, 2), "%")

def analyze_group(column, title):
    result = (
        known.groupby(column, dropna=False)
        .agg(
            total_orders=("order_id", "count"),
            rto_orders=("is_rto", "sum"),
            rto_rate=("is_rto", "mean")
        )
        .reset_index()
    )

    result["rto_rate"] = (result["rto_rate"] * 100).round(2)
    result = result.sort_values("total_orders", ascending=False)

    print("\n" + title)
    print(result.to_string(index=False))

    filename = column.replace(" ", "_") + "_analysis.csv"
    result.to_csv(OUTPUT_DIR / filename, index=False)

analyze_group("customer_prior_rto", "PREVIOUS RTO HISTORY")
analyze_group("customer_prior_orders", "PREVIOUS ORDER HISTORY")
analyze_group("city", "CITY ANALYSIS")
analyze_group("utm_source", "MARKETING SOURCE ANALYSIS")
analyze_group("courier", "COURIER ANALYSIS")

known["address_group"] = pd.cut(
    known["address_length"],
    bins=[-1, 15, 30, 45, 60, float("inf")],
    labels=["0-15", "16-30", "31-45", "46-60", "60+"]
)

analyze_group("address_group", "ADDRESS LENGTH ANALYSIS")

df.to_csv(OUTPUT_DIR / "cleaned_orders.csv", index=False)

print("\nAnalysis completed successfully!")
print("Results saved inside the analysis folder.")
