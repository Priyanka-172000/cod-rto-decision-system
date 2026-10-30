# Decision Log – COD RTO Decision System

**Project:** COD RTO Prevention System  
**Date:** 30 October 2026

This document records the major design decisions, alternatives considered, and reasons for selecting the final approach.

## 1. Data Cleaning

**Decision:** Remove exact duplicate rows before analysis.

- Original dataset: 2,018 rows.
- Exact duplicate rows removed: 30.
- Cleaned dataset: 1,988 rows.
- Known final outcomes: 1,987.

**Alternative considered:** Analyze all original rows.

**Reason selected:** Duplicate records could inflate order counts and distort RTO rates. Removing exact duplicates gives a more reliable analysis.

## 2. Rule-Based Decision Engine

**Decision:** Use Python rules for numerical and historical risk checks.

Rules include:

- Previous RTO count.
- Address length and completeness indicators.
- Order value.
- Configurable prepaid discount.
- Confirmation timeout.

**Alternative considered:** Ask an LLM to make every order decision.

**Reason selected:** Python is more predictable for numerical comparisons and financial calculations. It is easier to test and explain to operations staff.

## 3. Configurable Thresholds

**Decision:** Store thresholds in `config/rules.json`.

Current configuration includes:

- Short address threshold: 15 characters.
- High previous RTO threshold: 2.
- Confirmation timeout: 24 hours.
- Maximum reminders: 1.
- Prepaid discount: 5%.
- Minimum prepaid offer order value: ₹299.

**Alternative considered:** Hard-code all thresholds in Python.

**Reason selected:** A non-technical operations user can adjust thresholds without modifying application logic.

## 4. LLM Integration

**Decision:** Use Google Gemini for interpreting ambiguous customer names and delivery addresses, with local validation as a fallback.

**Alternative considered:** Use an LLM for all risk calculations and financial decisions.

**Reason selected:** LLMs can help interpret unstructured text, but deterministic code is better for exact numerical and financial calculations.

**Implementation note:** Gemini connectivity was tested successfully. The historical batch decision run used local fallback validation for all 1,988 orders; it did not send the full dataset to Gemini.

## 5. WhatsApp Mock

**Decision:** Build a Python-based WhatsApp response simulator rather than integrating a real WhatsApp account.

Supported responses:

- YES: confirm and proceed to shipping.
- NO: hold the order for cancellation review.
- PREPAID/PAY: prepare the prepaid offer.
- Random response: ask the customer to provide a valid reply.
- No response after 24 hours: hold for manual review.

**Alternative considered:** Integrate the live WhatsApp Business API.

**Reason selected:** The assignment permits a mock API or simple simulator. The simulator demonstrates the workflow without requiring external account setup.

## 6. Prepaid Discount

**Decision:** Offer a 5% prepaid discount.

For an average order value of ₹649:

- Discount = ₹649 × 5% = ₹32.45.
- Customer payable amount = ₹649 − ₹32.45 = ₹616.55.

**Alternative considered:** Offer a larger discount.

**Reason selected:** A modest discount encourages prepaid payment while limiting the cost of incentives.

## 7. Financial Impact Simulation

**Decision:** Use scenario assumptions to estimate potential RTO savings, lost contribution, and discount cost.

Assumptions:

- 30% RTO prevention in the confirmation group.
- 5% false cancellations among delivered orders in that group.
- 20% prepaid acceptance.
- 4% prepaid RTO rate.
- 5% prepaid discount.

**Result:** Estimated net impact of ₹24,704.55.

**Alternative considered:** Present all estimated savings as actual savings.

**Reason selected:** The simulation is not a controlled experiment. The assumptions must be validated through a pilot before reporting realized financial benefits.

## 8. Dashboard

**Decision:** Build a simple HTML dashboard generated using Python.

It displays:

- Four decision categories.
- Historical delivery and RTO outcomes.
- Estimated financial impact.
- Scenario breakdown.
- Important limitations.

**Alternative considered:** Build a complex analytics application.

**Reason selected:** A lightweight dashboard is easier to run and understand during the assignment review.

## 9. Customer Protection

**Decision:** Prefer confirmation and prepaid nudges over automatic cancellation for most risk indicators.

**Alternative considered:** Automatically cancel every high-risk COD order or block entire pincodes.

**Reason selected:** A first-time customer may be genuine even when their order has limited history. Selective verification balances Operations' RTO concerns with Marketing's customer acquisition concerns.

## 10. Future Improvements

- Test the engine on live incoming orders in shadow mode.
- Measure actual WhatsApp response and prepaid conversion rates.
- Add courier and regional risk monitoring with minimum sample-size checks.
- Validate Gemini decisions against human-reviewed examples.
- Add controlled experiments to measure actual financial impact.
