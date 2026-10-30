
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "analysis" / "decision_log.csv"
OUTPUT_FILE = BASE_DIR / "analysis" / "impact_simulation.csv"

# Assignment financial assumptions
AOV = 649
GROSS_MARGIN = 0.62
RTO_COST = 169.40

# Scenario assumptions, not measured results
CONFIRMATION_RTO_PREVENTION_RATE = 0.30
FALSE_CANCELLATION_RATE = 0.05
PREPAID_ACCEPTANCE_RATE = 0.20
PREPAID_RTO_RATE = 0.04
PREPAID_DISCOUNT_RATE = 0.05

df = pd.read_csv(DATA_FILE)

# Exclude orders without a known final outcome.
df["historical_status"] = (
    df["historical_status"].astype(str).str.strip().str.upper()
)

df = df[
    df["historical_status"].isin(["DELIVERED", "RTO"])
].copy()

rows = []
total_savings = 0.0
total_lost_contribution = 0.0
total_discount_cost = 0.0

# 1. Estimate the effect of WhatsApp confirmation.
confirmation = df[df["action"] == "WHATSAPP_CONFIRMATION"]

confirmation_rtos = int(
    (confirmation["historical_status"] == "RTO").sum()
)
confirmation_delivered = int(
    (confirmation["historical_status"] == "DELIVERED").sum()
)

avoided_rtos = (
    confirmation_rtos * CONFIRMATION_RTO_PREVENTION_RATE
)
false_cancellations = (
    confirmation_delivered * FALSE_CANCELLATION_RATE
)


confirmation_extra_contribution = (
    avoided_rtos * AOV * GROSS_MARGIN
)

confirmation_savings = (
    avoided_rtos * RTO_COST
    + confirmation_extra_contribution
)



confirmation_lost = (
    false_cancellations * AOV * GROSS_MARGIN
)

total_savings += confirmation_savings
total_lost_contribution += confirmation_lost

rows.append({
    "scenario": "WhatsApp confirmation",
    "eligible_orders": len(confirmation),
    "estimated_orders_affected": round(avoided_rtos, 2),
    "estimated_savings_inr": round(confirmation_savings, 2),
    "estimated_lost_contribution_inr": round(
        confirmation_lost, 2
    ),
    "estimated_discount_cost_inr": 0.0,
    "estimated_net_impact_inr": round(
        confirmation_savings - confirmation_lost, 2
    )
})

# 2. Estimate the effect of optional prepaid nudges.
prepaid = df[df["action"] == "NUDGE_TO_PREPAID"]

prepaid_orders = len(prepaid)
prepaid_rtos = int(
    (prepaid["historical_status"] == "RTO").sum()
)

historical_prepaid_bucket_rto_rate = (
    prepaid_rtos / prepaid_orders if prepaid_orders else 0
)

accepted_orders = prepaid_orders * PREPAID_ACCEPTANCE_RATE

rto_rate_reduction = max(
    0,
    historical_prepaid_bucket_rto_rate - PREPAID_RTO_RATE
)

avoided_prepaid_rtos = accepted_orders * rto_rate_reduction

# Estimate benefit when an order that would have RTO'd instead delivers.
prepaid_delivery_contribution = (
    AOV * GROSS_MARGIN
)

prepaid_savings = avoided_prepaid_rtos * RTO_COST
prepaid_extra_contribution = (
    avoided_prepaid_rtos * prepaid_delivery_contribution
)
prepaid_discount_cost = (
    accepted_orders * AOV * PREPAID_DISCOUNT_RATE
)

prepaid_net = (
    prepaid_savings
    + prepaid_extra_contribution
    - prepaid_discount_cost
)

total_savings += prepaid_savings + prepaid_extra_contribution
total_discount_cost += prepaid_discount_cost

rows.append({
    "scenario": "Prepaid nudge",
    "eligible_orders": prepaid_orders,
    "estimated_orders_affected": round(
        avoided_prepaid_rtos, 2
    ),
    "estimated_savings_inr": round(
        prepaid_savings + prepaid_extra_contribution, 2
    ),
    "estimated_lost_contribution_inr": 0.0,
    "estimated_discount_cost_inr": round(
        prepaid_discount_cost, 2
    ),
    "estimated_net_impact_inr": round(prepaid_net, 2)
})

# 3. Combine both scenarios.
combined_net = (
    total_savings
    - total_lost_contribution
    - total_discount_cost
)

rows.append({
    "scenario": "Combined estimated impact",
    "eligible_orders": len(df),
    "estimated_orders_affected": round(
        avoided_rtos + avoided_prepaid_rtos, 2
    ),
    "estimated_savings_inr": round(total_savings, 2),
    "estimated_lost_contribution_inr": round(
        total_lost_contribution, 2
    ),
    "estimated_discount_cost_inr": round(
        total_discount_cost, 2
    ),
    "estimated_net_impact_inr": round(combined_net, 2)
})

result = pd.DataFrame(rows)
result.to_csv(OUTPUT_FILE, index=False)

print("IMPACT SIMULATION — SCENARIO ESTIMATES")
print("=" * 55)
print(result.to_string(index=False))

print("\nAssumptions used:")
print(
    f"Confirmation prevents {CONFIRMATION_RTO_PREVENTION_RATE:.0%} "
    "of RTOs in the confirmation bucket."
)
print(
    f"False cancellations affect {FALSE_CANCELLATION_RATE:.0%} "
    "of delivered orders in that bucket."
)
print(f"Prepaid acceptance rate: {PREPAID_ACCEPTANCE_RATE:.0%}")
print(f"Assumed prepaid RTO rate: {PREPAID_RTO_RATE:.0%}")
print(f"Prepaid discount: {PREPAID_DISCOUNT_RATE:.0%}")

print("\nSaved simulation to:", OUTPUT_FILE)
print(
    "\nIMPORTANT: This is a hypothetical scenario, not a measured "
    "or guaranteed saving. Validate the assumptions with a pilot."
)
