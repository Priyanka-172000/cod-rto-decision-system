# AI Usage Log – COD RTO Decision System

**Project:** COD RTO Prevention System  
**Date:** 30 October 2026

## 1. AI Tools Used

| Tool              | Purpose                                                                           | Usage                              |
| ----------------- | --------------------------------------------------------------------------------- | ---------------------------------- |
| ChatGPT           | Planning, coding assistance, debugging, documentation and analysis interpretation | Used throughout development        |
| Google Gemini API | Customer name and address text validation                                         | API connection tested successfully |
| Python            | Data processing, decision rules and financial calculations                        | Used for deterministic processing  |
| pandas            | Dataset cleaning and group-level RTO analysis                                     | Used for historical analysis       |

## 2. How AI Was Used

### ChatGPT

- Helped structure the project into separate Python modules.
- Assisted with decision-engine logic.
- Helped debug Python and environment issues.
- Assisted with dashboard and business memo development.
- Helped interpret historical RTO patterns.

### Google Gemini

- Integrated through the Google GenAI Python SDK.
- Intended for interpreting ambiguous names and delivery addresses.
- Prompt designed to identify placeholder names and incomplete or generic addresses.
- Designed to avoid treating unfamiliar regional names as automatically suspicious.

**Validation status:** A Gemini API connection test completed successfully. The historical batch run used `LOCAL_FALLBACK` for all 1,988 orders. Therefore, Gemini was not used to classify the historical dataset.

### Python and pandas

These handled:

- Duplicate removal.
- Missing-value checks.
- RTO percentage calculations.
- Customer-history analysis.
- City, courier and marketing-source analysis.
- Financial scenario calculations.

## 3. AI Limitations, Weak Approaches and Corrections

The following examples document issues and failure modes identified during development and validation. They are not claims of measured production failures.

### Example 1 – Using an LLM for numerical risk decisions

**Weak approach:** Allowing an LLM to calculate RTO percentages, shipping costs or decide thresholds.

**Why it is weak:** LLM responses can be inconsistent for exact calculations and numerical comparisons.

**Correction:** Implemented these calculations and threshold checks in Python. The LLM is reserved for interpreting unstructured customer text.

### Example 2 – Treating every short address as invalid

**Potential weak output:** A short address could be classified as invalid even when it contains a valid, locally understood delivery location.

**Why it matters:** The historical analysis found a 61.75% RTO rate for addresses of 0–15 characters, but this does not prove every short address is invalid.

**Correction:** Short addresses trigger verification or WhatsApp confirmation rather than automatic cancellation. Regional and Hinglish address interpretation is treated as a text-validation task.

### Example 3 – Treating unfamiliar names as fake

**Potential weak output:** A name unfamiliar to the model could be incorrectly flagged as suspicious.

**Why it matters:** Regional names and spelling variations should not be treated as evidence of fraud.

**Correction:** The Gemini prompt instructs the model not to flag unfamiliar names solely because they are uncommon. Local fallback checks focus on known placeholder patterns such as `asdf`, `test` and `dummy`.

## 4. API and Reliability Notes

- An OpenAI API test was attempted but returned HTTP 429 because the account had no available API credits.
- Google Gemini was selected as an alternative.
- The Gemini connection test succeeded.
- Local validation remains available if the Gemini API is unavailable or returns an error.
- API keys are stored in `.env` and must not be committed to GitHub.

## 5. Human Oversight

AI validation is advisory. The system uses deterministic Python rules for numerical decisions and keeps manual review for missing addresses and unresponsive confirmation cases.

Before production use, AI classifications should be evaluated against human-reviewed examples, including regional names, Hinglish addresses and valid short addresses.

## 6. Overall Conclusion

AI accelerated development and supports interpretation of unstructured customer information. Deterministic Python logic remains responsible for numerical risk checks, configurable decisions and financial calculations. This separation improves transparency, reliability and auditability.
