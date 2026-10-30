
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "analysis" / "cleaned_orders.csv"
OUTPUT_FILE = BASE_DIR / "analysis" / "financial_impact.csv"

# Assignment assumptions
AOV = 649
GROSS_MARGIN_RATE = 0.62
FORWARD_SHIPPING_COST = 65
RETURN_SHIPPING_COST = 65
HANDLING_COST = 25
DAMAGE_PROBABILITY = 0.08
DAMAGE_COST = 180

RTO_COST = (
    FORWARD_SHIPPING_COST
    + RETURN_SHIPPING_COST
    + HANDLING_COST
    + DAMAGE_PROBABILITY * DAMAGE_COST
)

DELIVERED_CONTRIBUTION = AOV * GROSS_MARGIN_RATE

df = pd.read_csv(DATA_FILE)

# Only orders with known final outcomes are used.
known = df[
    df["final_status"].astype(str).str.strip().str.upper().isin(
        ["DELIVERED", "RTO"]
    )
].copy()

known["final_status"] = (
    known["final_status"].astype(str).str.strip().str.upper()
)

total_orders = len(known)
delivered = int((known["final_status"] == "DELIVERED").sum())
rto = int((known["final_status"] == "RTO").sum())

historical_rto_rate = rto / total_orders if total_orders else 0
historical_rto_cost = rto * RTO_COST
delivered_contribution_total = delivered * DELIVERED_CONTRIBUTION

results = [
    ("Orders with known outcomes", total_orders, "orders"),
    ("Delivered orders", delivered, "orders"),
    ("RTO orders", rto, "orders"),
    ("Historical RTO rate", round(historical_rto_rate * 100, 2), "%"),
    ("Estimated cost per RTO", round(RTO_COST, 2), "INR"),
    ("Estimated historical RTO cost", round(historical_rto_cost, 2), "INR"),
    (
        "Estimated contribution from delivered orders",
        round(delivered_contribution_total, 2),
        "INR",
    ),
]

output = pd.DataFrame(results, columns=["metric", "value", "unit"])
output.to_csv(OUTPUT_FILE, index=False)

print("HISTORICAL FINANCIAL BASELINE")
print("-" * 45)
for metric, value, unit in results:
    if unit == "INR":
        print(f"{metric}: ₹{value:,.2f}")
    elif unit == "%":
        print(f"{metric}: {value}%")
    else:
        print(f"{metric}: {value:,}")

print("\nSaved financial baseline to:", OUTPUT_FILE)
print(
    "\nNote: These are estimates based on assignment assumptions. "
    "They do not prove that the decision engine saved this amount."
)
