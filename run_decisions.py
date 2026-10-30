
import json
from pathlib import Path

import pandas as pd

from decision_engine import decide_order

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "analysis" / "cleaned_orders.csv"
OUTPUT_DIR = BASE_DIR / "analysis"
OUTPUT_FILE = OUTPUT_DIR / "decision_log.csv"

OUTPUT_DIR.mkdir(exist_ok=True)

# Load historical data
df = pd.read_csv(
    DATA_FILE,
    dtype={"pincode": "string"}
)

df["final_status"] = (
    df["final_status"]
    .astype("string")
    .str.strip()
    .str.upper()
)

decisions = []

print("PROCESSING HISTORICAL COD ORDERS")
print("=" * 55)

for index, row in df.iterrows():

    order = row.to_dict()

    # Historical analysis uses local validation.
    # No Gemini API calls are made for the historical batch.
    decision = decide_order(
        order,
        use_llm=False
    )

    decisions.append({
        "order_id": decision["order_id"],
        "action": decision["action"],

        "risk_flags": json.dumps(
            decision["risk_flags"]
        ),

        "reasons": json.dumps(
            decision["reasons"]
        ),

        "ai_validation_status":
            decision["ai_validation_status"],

        "ai_validation_source":
            decision["ai_validation_source"],

        "ai_validation_confidence":
            decision["ai_validation_confidence"],

        "ai_validation_reason":
            decision["ai_validation_reason"],

        "prepaid_discount_percent":
            decision["prepaid_discount_percent"],

        "confirmation_timeout_hours":
            decision["confirmation_timeout_hours"],

        "historical_status": row["final_status"],
        "order_value": row["order_value"],
        "payment_method": row["payment_method"]
    })

    if (index + 1) % 500 == 0:
        print(f"Processed {index + 1} orders...")


# Create decision log
decision_df = pd.DataFrame(decisions)

decision_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nDECISION ENGINE RESULTS")
print("=" * 55)

print("Orders evaluated:", len(decision_df))

print("\nAction counts:")
print(
    decision_df["action"]
    .value_counts()
    .to_string()
)

print("\nAI validation sources:")
print(
    decision_df["ai_validation_source"]
    .value_counts()
    .to_string()
)

print("\nHistorical outcomes:")
print(
    decision_df["historical_status"]
    .value_counts()
    .to_string()
)

print("\nDecision log saved to:", OUTPUT_FILE)
