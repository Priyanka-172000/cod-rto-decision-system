
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from llm_validator import validate_customer_details, local_validate

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
RULES_FILE = BASE_DIR / "config" / "rules.json"


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def safe_int(value, default=0):
    try:
        if value is None or str(value).strip().lower() in (
            "", "nan", "none"
        ):
            return default

        return int(float(value))

    except (ValueError, TypeError):
        return default


def is_missing(value):
    return (
        value is None
        or str(value).strip().lower() in ("", "nan", "none")
    )


# --------------------------------------------------
# DECISION ENGINE
# --------------------------------------------------

def decide_order(order, use_llm=None):

    rules = load_rules()

    address = (
        ""
        if is_missing(order.get("address"))
        else str(order.get("address")).strip()
    )

    customer_name = order.get("customer_name", "")

    prior_rto = safe_int(order.get("customer_prior_rto"))
    order_value = safe_int(order.get("order_value"))

    risk_flags = []
    reasons = []

    ai_validation = {
        "status": "NOT_RUN",
        "risk_flags": [],
        "reason": "AI validation was not required.",
        "confidence": 0,
        "source": "NOT_USED"
    }

    address_missing = not address

    short_address = (
        bool(address)
        and len(address) <=
        rules["address"]["short_address_max_chars"]
    )

    high_rto = (
        prior_rto >=
        rules["customer_history"]["high_rto_count"]
    )

    # --------------------------------------------------
    # 1. BASIC PYTHON VALIDATION
    # --------------------------------------------------

    if address_missing:
        risk_flags.append("MISSING_ADDRESS")
        reasons.append("Delivery address is missing.")

    elif short_address:
        risk_flags.append("SHORT_ADDRESS")
        reasons.append("Delivery address needs verification.")

    if high_rto:
        risk_flags.append("HIGH_PREVIOUS_RTO")
        reasons.append(
            f"Customer has {prior_rto} previous RTO orders."
        )

    # --------------------------------------------------
    # 2. GEMINI / LOCAL CUSTOMER DETAIL VALIDATION
    # --------------------------------------------------

    # Run text validation only when details need checking.
    # Historical batch processing can explicitly disable Gemini.

    needs_text_validation = (
        address_missing or short_address
        or bool(str(customer_name or "").strip())
    )

    if needs_text_validation:

        # The dataset may not contain customer names.
        # Do not falsely label a missing dataset field as a
        # suspicious customer name.
        name_for_validation = (
            customer_name
            if not is_missing(customer_name)
            else "Name not available in dataset"
        )

        ai_validation = validate_customer_details(
            name_for_validation,
            address,
            use_llm=use_llm
        )

        for flag in ai_validation.get("risk_flags", []):
            if flag not in risk_flags:
                risk_flags.append(flag)

        if ai_validation["status"] == "REVIEW":
            reasons.append(
                "Customer details need verification: "
                + ai_validation["reason"]
            )

    # --------------------------------------------------
    # 3. DECISION PRIORITY
    # --------------------------------------------------

    if address_missing:

        action = rules["decision"]["missing_address_action"]

        reasons.append(
            "Hold the order for manual address verification."
        )

    elif high_rto and rules["customer_history"][
        "require_confirmation_for_high_rto"
    ]:

        action = rules["decision"]["high_risk_action"]

        reasons.append(
            "Customer confirmation is required before dispatch."
        )

    elif (
        ai_validation["status"] == "REVIEW"
        or short_address
    ):

        action = rules["decision"]["short_address_action"]

        reasons.append(
            "Ask the customer to confirm or correct the delivery details."
        )

    elif (
        prior_rto == 1
        and order_value >=
        rules["prepaid"]["minimum_order_value"]
    ):

        action = "NUDGE_TO_PREPAID"

        reasons.append(
            "Offer optional prepaid payment with a discount."
        )

    else:

        action = "SHIP_AS_IS"

        reasons.append(
            "No configured rule requires additional verification."
        )

    # --------------------------------------------------
    # 4. RETURN DECISION
    # --------------------------------------------------

    return {
        "order_id": str(order.get("order_id", "UNKNOWN")),
        "action": action,
        "risk_flags": risk_flags,
        "reasons": reasons,

        "ai_validation_status": ai_validation["status"],
        "ai_validation_source": ai_validation["source"],
        "ai_validation_confidence": ai_validation["confidence"],
        "ai_validation_reason": ai_validation["reason"],

        "prepaid_discount_percent": (
            rules["prepaid"]["discount_percent"]
            if action == "NUDGE_TO_PREPAID"
            else 0
        ),

        "confirmation_timeout_hours": (
            rules["confirmation"]["timeout_hours"]
            if action == "WHATSAPP_CONFIRMATION"
            else None
        )
    }


# --------------------------------------------------
# 5. SAMPLE TESTS
# --------------------------------------------------

if __name__ == "__main__":

    sample_orders = [
        {
            "order_id": "TEST001",
            "customer_name": "asdf",
            "address": "12 MG Road",
            "customer_prior_rto": 0,
            "order_value": 649
        },
        {
            "order_id": "TEST002",
            "customer_name": "Rahul Sharma",
            "address": "Flat 12, Lake View Apartments, Main Road",
            "customer_prior_rto": 2,
            "order_value": 999
        },
        {
            "order_id": "TEST003",
            "customer_name": "Priya Patil",
            "address": "Near bus stop",
            "customer_prior_rto": 1,
            "order_value": 649
        },
        {
            "order_id": "TEST004",
            "customer_name": "Ananya Rao",
            "address": "Flat 203, Green Park Apartments, MG Road",
            "customer_prior_rto": 1,
            "order_value": 649
        },
        {
            "order_id": "TEST005",
            "customer_name": "",
            "address": "",
            "customer_prior_rto": 0,
            "order_value": 649
        }
    ]

    # Avoid API calls unless explicitly requested.
    use_live_gemini = os.getenv(
        "USE_LLM_FOR_SAMPLE_TESTS", "false"
    ).lower() == "true"

    for order in sample_orders:

        decision = decide_order(
            order,
            use_llm=use_live_gemini
        )

        print(json.dumps(decision, indent=2))
        print("-" * 55)
