
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RULES_FILE = BASE_DIR / "config" / "rules.json"


def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_prepaid_offer(order_value, discount_percent):
    discount = round(order_value * discount_percent / 100, 2)
    payable = round(order_value - discount, 2)

    return {
        "original_amount": round(order_value, 2),
        "discount": discount,
        "payable_amount": payable
    }


def simulate_whatsapp_response(response, order_value=649):
    rules = load_rules()
    response = str(response).strip().upper()

    if response in ("YES", "Y"):
        return {
            "status": "CONFIRMED",
            "next_action": "SHIP_ORDER",
            "message": "Thank you! Your order is confirmed and will be processed."
        }

    if response in ("NO", "N"):
        return {
            "status": "CUSTOMER_DECLINED",
            "next_action": "CANCEL_AFTER_REVIEW",
            "message": "Your order will be held while we review your cancellation request."
        }

    if response in ("PREPAID", "PAY"):
        discount_percent = rules["prepaid"]["discount_percent"]
        offer = calculate_prepaid_offer(order_value, discount_percent)

        return {
            "status": "PREPAID_OFFER_ACCEPTED",
            "next_action": "INITIATE_PREPAID_PAYMENT",
            "message": "Your prepaid offer is ready.",
            "offer": offer
        }

    if response in ("", "NO_REPLY", "TIMEOUT"):
        timeout = rules["confirmation"]["timeout_hours"]

        return {
            "status": "NO_RESPONSE",
            "next_action": "HOLD_FOR_REVIEW",
            "timeout_hours": timeout,
            "message": (
                f"No response received within {timeout} hours. "
                "Hold dispatch and send the order for review."
            )
        }

    return {
        "status": "UNRECOGNIZED_REPLY",
        "next_action": "ASK_FOR_VALID_REPLY",
        "message": (
            "Sorry, I couldn't understand your reply. "
            "Please reply YES to confirm or NO to decline."
        )
    }


if __name__ == "__main__":
    test_responses = ["YES", "NO", "maybe", "NO_REPLY", "PREPAID"]

    for response in test_responses:
        print(f"\nCustomer response: {response}")
        result = simulate_whatsapp_response(response)
        print(json.dumps(result, indent=2))
