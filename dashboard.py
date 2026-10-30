
from pathlib import Path
from html import escape

import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

ANALYSIS_DIR = BASE_DIR / "analysis"

DECISIONS_FILE = ANALYSIS_DIR / "decision_log.csv"
IMPACT_FILE = ANALYSIS_DIR / "impact_simulation.csv"

OUTPUT_FILE = BASE_DIR / "dashboard.html"


# --------------------------------------------------
# 2. LOAD PROJECT OUTPUTS
# --------------------------------------------------

if not DECISIONS_FILE.exists():
    raise FileNotFoundError(
        "decision_log.csv not found. "
        "Run python run_decisions.py first."
    )

if not IMPACT_FILE.exists():
    raise FileNotFoundError(
        "impact_simulation.csv not found. "
        "Run python simulate_impact.py first."
    )

decisions = pd.read_csv(DECISIONS_FILE)
impact = pd.read_csv(IMPACT_FILE)

if decisions.empty:
    raise ValueError("No decision records available.")

if "action" not in decisions.columns:
    raise ValueError("The decision log has no action column.")


# --------------------------------------------------
# 3. DECISION DISTRIBUTION
# --------------------------------------------------

all_actions = [
    "SHIP_AS_IS",
    "WHATSAPP_CONFIRMATION",
    "NUDGE_TO_PREPAID",
    "HOLD_CANCEL_REVIEW"
]

action_labels = {
    "SHIP_AS_IS": "Ship as-is",
    "WHATSAPP_CONFIRMATION": "WhatsApp confirmation",
    "NUDGE_TO_PREPAID": "Nudge to prepaid",
    "HOLD_CANCEL_REVIEW": "Hold / cancel review"
}

action_colors = {
    "SHIP_AS_IS": "#198754",
    "WHATSAPP_CONFIRMATION": "#2563eb",
    "NUDGE_TO_PREPAID": "#d97706",
    "HOLD_CANCEL_REVIEW": "#dc3545"
}

decisions["action"] = (
    decisions["action"]
    .astype(str)
    .str.strip()
    .str.upper()
)

action_counts = decisions["action"].value_counts()

total_decisions = len(decisions)

action_cards = ""

for action in all_actions:

    count = int(action_counts.get(action, 0))

    label = action_labels[action]

    percentage = (
        count / total_decisions * 100
        if total_decisions else 0
    )

    color = action_colors[action]

    action_cards += f"""
    <div class="metric-card">
        <div class="muted">{escape(label)}</div>

        <div class="number">{count:,}</div>

        <div class="muted">
            {percentage:.1f}% of evaluated orders
        </div>

        <div class="bar-bg">
            <div class="bar"
                 style="width:{percentage:.2f}%;background:{color}">
            </div>
        </div>
    </div>
    """


# --------------------------------------------------
# 4. HISTORICAL OUTCOMES
# --------------------------------------------------

if "historical_status" not in decisions.columns:
    raise ValueError(
        "historical_status column missing from decision_log.csv."
    )

statuses = (
    decisions["historical_status"]
    .astype(str)
    .str.strip()
    .str.upper()
)

known_mask = statuses.isin(["DELIVERED", "RTO"])

known_statuses = statuses[known_mask]

known_count = int(known_mask.sum())

delivered = int(
    (known_statuses == "DELIVERED").sum()
)

rto = int(
    (known_statuses == "RTO").sum()
)

in_transit = int(
    (statuses == "IN_TRANSIT").sum()
)

unknown = total_decisions - known_count - in_transit

rto_rate = (
    rto / known_count * 100
    if known_count else 0
)


# --------------------------------------------------
# 5. FINANCIAL IMPACT
# --------------------------------------------------

required_impact_columns = [
    "scenario",
    "eligible_orders",
    "estimated_savings_inr",
    "estimated_lost_contribution_inr",
    "estimated_discount_cost_inr",
    "estimated_net_impact_inr"
]

missing_columns = [
    column
    for column in required_impact_columns
    if column not in impact.columns
]

if missing_columns:
    raise ValueError(
        f"Missing financial columns: {missing_columns}"
    )

combined_rows = impact[
    impact["scenario"] == "Combined estimated impact"
]

if combined_rows.empty:
    raise ValueError(
        "Combined estimated impact not found. "
        "Run simulate_impact.py first."
    )

combined = combined_rows.iloc[0]

benefit = float(combined["estimated_savings_inr"])

lost = float(
    combined["estimated_lost_contribution_inr"]
)

discount = float(
    combined["estimated_discount_cost_inr"]
)

net = float(
    combined["estimated_net_impact_inr"]
)


# --------------------------------------------------
# 6. RUPEE FORMATTING
# --------------------------------------------------

def rupees(value):
    return f"₹{float(value):,.2f}"


# --------------------------------------------------
# 7. SCENARIO BREAKDOWN TABLE
# --------------------------------------------------

scenario_rows = ""

for _, row in impact.iterrows():

    scenario_rows += f"""
    <tr>
        <td>{escape(str(row["scenario"]))}</td>

        <td>{int(row["eligible_orders"]):,}</td>

        <td>
            {rupees(row["estimated_savings_inr"])}
        </td>

        <td>
            {rupees(row["estimated_lost_contribution_inr"])}
        </td>

        <td>
            {rupees(row["estimated_discount_cost_inr"])}
        </td>

        <td>
            <strong>
                {rupees(row["estimated_net_impact_inr"])}
            </strong>
        </td>
    </tr>
    """


# --------------------------------------------------
# 8. GENERATE DASHBOARD HTML
# --------------------------------------------------

html = f"""<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>COD RTO Decision Dashboard</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f3f5f9;
    color: #182230;
}}

header {{
    background: #172554;
    color: white;
    padding: 28px 5%;
}}

header h1 {{
    margin: 0 0 8px;
}}

header p {{
    margin: 0;
    color: #dbeafe;
}}

main {{
    max-width: 1200px;
    margin: 24px auto;
    padding: 0 20px 40px;
}}

h2 {{
    margin-top: 30px;
    margin-bottom: 16px;
}}

.grid {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(210px, 1fr));
    gap: 16px;
}}

.metric-card {{
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px #0000000a;
}}

.number {{
    font-size: 30px;
    font-weight: 700;
    margin: 10px 0;
    overflow-wrap: anywhere;
}}

.muted {{
    color: #667085;
    font-size: 14px;
}}

.bar-bg {{
    margin-top: 14px;
    height: 8px;
    background: #e5e7eb;
    border-radius: 6px;
    overflow: hidden;
}}

.bar {{
    height: 100%;
    border-radius: 6px;
}}

.panel {{
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-top: 16px;
    overflow-x: auto;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    min-width: 760px;
}}

th, td {{
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #eaecf0;
    font-size: 14px;
}}

th {{
    background: #f9fafb;
}}

.net {{
    color: #15803d;
}}

.notice {{
    background: #fff7ed;
    border-left: 5px solid #ea580c;
    padding: 16px;
    border-radius: 8px;
    line-height: 1.6;
    margin-top: 18px;
}}

footer {{
    margin-top: 25px;
    color: #667085;
    font-size: 13px;
    line-height: 1.5;
}}

@media (max-width: 600px) {{

    header {{
        padding: 22px;
    }}

    main {{
        padding: 0 12px 30px;
    }}

    .number {{
        font-size: 25px;
    }}

}}

</style>

</head>

<body>

<header>

    <h1>COD RTO Decision Dashboard</h1>

    <p>
        Order risk analysis, decision distribution
        and financial scenarios
    </p>

</header>

<main>

    <!-- DECISION DISTRIBUTION -->

    <h2>Decision Distribution</h2>

    <div class="grid">

        {action_cards}

    </div>


    <!-- HISTORICAL OUTCOMES -->

    <h2>Historical Outcomes</h2>

    <div class="grid">

        <div class="metric-card">

            <div class="muted">
                Orders evaluated
            </div>

            <div class="number">
                {total_decisions:,}
            </div>

        </div>


        <div class="metric-card">

            <div class="muted">
                Known final outcomes
            </div>

            <div class="number">
                {known_count:,}
            </div>

        </div>


        <div class="metric-card">

            <div class="muted">
                Delivered orders
            </div>

            <div class="number">
                {delivered:,}
            </div>

        </div>


        <div class="metric-card">

            <div class="muted">
                RTO orders
            </div>

            <div class="number">
                {rto:,}
            </div>

            <div class="muted">
                Historical RTO rate: {rto_rate:.2f}%
            </div>

        </div>


        <div class="metric-card">

            <div class="muted">
                In-transit orders
            </div>

            <div class="number">
                {in_transit:,}
            </div>

        </div>


        <div class="metric-card">

            <div class="muted">
                Unknown outcomes
            </div>

            <div class="number">
                {unknown:,}
            </div>

        </div>

    </div>


    <!-- FINANCIAL IMPACT -->

    <h2>Estimated Financial Impact</h2>

    <div class="grid">

        <div class="metric-card">

            <div class="muted">
                Estimated total benefits
            </div>

            <div class="number">
                {rupees(benefit)}
            </div>

            <div class="muted">
                Includes estimated RTO costs
                and delivery contribution
            </div>

        </div>


        <div class="metric-card">

            <div class="muted">
                Potential lost contribution
            </div>

            <div class="number">
                {rupees(lost)}
            </div>

        </div>


        <div class="metric-card">

            <div class="muted">
                Prepaid discount cost
            </div>

            <div class="number">
                {rupees(discount)}
            </div>

        </div>


        <div class="metric-card">

            <div class="muted">
                Estimated net impact
            </div>

            <div class="number net">
                {rupees(net)}
            </div>

        </div>

    </div>


    <!-- SCENARIO TABLE -->

    <div class="panel">

        <h3>Scenario Breakdown (INR)</h3>

        <table>

            <thead>

                <tr>

                    <th>Scenario</th>

                    <th>Eligible orders</th>

                    <th>Estimated benefits</th>

                    <th>Lost contribution</th>

                    <th>Discount cost</th>

                    <th>Net impact</th>

                </tr>

            </thead>

            <tbody>

                {scenario_rows}

            </tbody>

        </table>

    </div>


    <!-- LIMITATIONS -->

    <div class="notice">

        <strong>Important Limitations:</strong>

        Financial impact is a hypothetical scenario,
        not verified savings.

        Confirmation effectiveness, false-cancellation
        rate, prepaid acceptance and prepaid RTO rates
        are assumptions that need a controlled pilot.

        The supplied sample contains COD orders only,
        so prepaid outcomes are simulated.

        Historical associations do not prove causation.

    </div>


    <!-- FOOTER -->

    <footer>

        Generated from decision_log.csv and
        impact_simulation.csv.

        <br>

        Run the Python analysis and simulation scripts
        again after updating the decision rules.

        <br>

        Historical data is not a live daily report.

    </footer>

</main>

</body>

</html>
"""


# --------------------------------------------------
# 9. SAVE DASHBOARD
# --------------------------------------------------

OUTPUT_FILE.write_text(
    html,
    encoding="utf-8"
)

print("=" * 55)
print("COD RTO DECISION DASHBOARD")
print("=" * 55)

print("Orders evaluated:", total_decisions)

print("\nDecision distribution:")

for action in all_actions:

    count = int(action_counts.get(action, 0))

    print(
        f"{action_labels[action]}: {count:,}"
    )

print("\nHistorical outcomes:")

print("Delivered:", delivered)
print("RTO:", rto)
print("In transit:", in_transit)

print("\nEstimated net impact:", rupees(net))

print("\nDashboard created successfully.")

print("Open this file in your browser:")

print(OUTPUT_FILE)
