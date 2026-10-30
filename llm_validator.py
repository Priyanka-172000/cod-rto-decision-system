
import json
import os
import re
import sys

from dotenv import load_dotenv
from google import genai

load_dotenv()


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "")

SUSPICIOUS_NAMES = {
    "asdf", "test", "testing", "abc", "xyz",
    "dummy", "unknown", "qwerty", "null", "none"
}

GENERIC_ADDRESS_PHRASES = [
    "near temple",
    "near bus stop",
    "near shop",
    "near school",
    "mandir ke samne",
    "mandir ke paas",
    "bus stop ke paas",
    "dukan ke paas",
    "ghar ke paas",
    "school ke samne"
]


# --------------------------------------------------
# 1. LOCAL FALLBACK VALIDATOR
# --------------------------------------------------

def local_validate(customer_name, address):

    name = str(customer_name or "").strip()
    address = str(address or "").strip()

    flags = []
    reasons = []

    normalized_name = re.sub(
        r"[^a-zA-Z0-9]",
        "",
        name.lower()
    )

    if not normalized_name:
        flags.append("MISSING_CUSTOMER_NAME")
        reasons.append("Customer name is missing.")

    elif normalized_name in SUSPICIOUS_NAMES:
        flags.append("SUSPICIOUS_CUSTOMER_NAME")
        reasons.append(
            "Customer name looks like placeholder or test text."
        )

    if not address:
        flags.append("MISSING_ADDRESS")
        reasons.append("Delivery address is missing.")

    elif len(address) < 15:
        flags.append("SHORT_ADDRESS")
        reasons.append(
            "Address is too short and needs verification."
        )

    else:
        lower_address = address.lower()

        if any(
            phrase in lower_address
            for phrase in GENERIC_ADDRESS_PHRASES
        ):
            flags.append("GENERIC_LANDMARK_ADDRESS")
            reasons.append(
                "Address contains a generic landmark "
                "without enough delivery details."
            )

    if flags:
        status = "REVIEW"
        confidence = 0.90
        reason = " ".join(reasons)
    else:
        status = "OK"
        confidence = 0.65
        reason = (
            "No obvious text-quality issue was detected "
            "by the local validation rules."
        )

    return {
        "status": status,
        "risk_flags": flags,
        "reason": reason,
        "confidence": confidence,
        "source": "LOCAL_FALLBACK"
    }


# --------------------------------------------------
# 2. GEMINI LLM VALIDATOR
# --------------------------------------------------

def gemini_validate(customer_name, address):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    if not GEMINI_MODEL:
        raise ValueError("GEMINI_MODEL is missing from .env")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You validate delivery details for a Cash on Delivery order.

Customer name: {customer_name}
Delivery address: {address}

Evaluate the details carefully.

Tasks:
1. Identify obviously fake or placeholder names.
2. Check whether the address contains useful delivery details.
3. Understand English and Hinglish address descriptions.
4. Identify generic landmark-only addresses.
5. Do not assume a name is fake just because it is unfamiliar
   or written in a regional language.
6. Do not invent missing address information.
7. Do not treat a short but valid Indian address as proof of fraud.
8. Recommend REVIEW when delivery details need verification.

Return ONLY valid JSON in this format:

{{
    "status": "OK or REVIEW",
    "risk_flags": [],
    "reason": "Short explanation for an operations employee",
    "confidence": 0.0
}}

Confidence must be between 0 and 1.
Do not include Markdown or code fences.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    raw_output = (response.text or "").strip()

    if not raw_output:
        raise ValueError("Gemini returned an empty response.")

    # Remove optional Markdown code fences
    raw_output = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        raw_output,
        flags=re.IGNORECASE
    ).strip()

    result = json.loads(raw_output)

    status = str(
        result.get("status", "REVIEW")
    ).upper()

    if status not in ("OK", "REVIEW"):
        status = "REVIEW"

    flags = result.get("risk_flags", [])

    if not isinstance(flags, list):
        flags = ["INVALID_LLM_RESPONSE"]

    try:
        confidence = float(result.get("confidence", 0))
    except (ValueError, TypeError):
        confidence = 0.0

    confidence = max(0.0, min(1.0, confidence))

    return {
        "status": status,
        "risk_flags": [str(flag) for flag in flags],
        "reason": str(
            result.get(
                "reason",
                "Manual verification recommended."
            )
        ),
        "confidence": confidence,
        "source": "GEMINI_LLM"
    }


# --------------------------------------------------
# 3. MAIN VALIDATION FUNCTION
# --------------------------------------------------

def validate_customer_details(
    customer_name,
    address,
    use_llm=None
):

    if use_llm is None:
        use_llm = USE_LLM

    if use_llm:
        try:
            return gemini_validate(
                customer_name,
                address
            )

        except Exception as error:
            print(
                "Gemini unavailable. Using local fallback:",
                str(error)
            )

    return local_validate(
        customer_name,
        address
    )


# --------------------------------------------------
# 4. TEST CASES
# --------------------------------------------------

if __name__ == "__main__":

    live_test = "--live" in sys.argv

    test_customers = [
        {
            "name": "asdf",
            "address": "12 MG Road"
        },
        {
            "name": "Rahul Sharma",
            "address": "Near temple"
        },
        {
            "name": "Priya Patil",
            "address": "Ghar mandir ke samne hai"
        },
        {
            "name": "Ananya Rao",
            "address": (
                "Flat 203, Green Park Apartments, "
                "MG Road, Bengaluru, Karnataka"
            )
        },
        {
            "name": "",
            "address": ""
        }
    ]

    print("\nCUSTOMER DETAIL VALIDATION")
    print("=" * 55)

    if live_test:
        print("MODE: GEMINI API (may use API quota)")
    else:
        print("MODE: LOCAL FALLBACK (no API request)")

    for customer in test_customers:

        result = validate_customer_details(
            customer["name"],
            customer["address"],
            use_llm=live_test
        )

        print("\nCustomer:", customer["name"])
        print("Address:", customer["address"])

        print(json.dumps(result, indent=4))
        print("-" * 55)
