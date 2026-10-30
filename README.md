# COD RTO Decision System

An AI-assisted Cash on Delivery (COD) risk analysis and decision-support system for a Direct-to-Consumer (D2C) e-commerce business.

The system evaluates historical COD orders, identifies risk indicators, recommends an action for each order, simulates WhatsApp confirmation responses, and estimates the financial impact of reducing Return to Origin (RTO).

## Business Problem

The business experiences approximately 28% COD RTO. Each RTO creates shipping, handling and potential product-damage costs.

The goal is to reduce avoidable RTO while protecting genuine customers from unnecessary order cancellations.

## Key Features

- Historical COD order data cleaning and analysis.
- Rule-based order decision engine.
- Customer name and address text validation using Gemini with local fallback.
- Configurable decision thresholds through JSON.
- WhatsApp response simulator.
- Prepaid discount calculator.
- Financial impact scenario simulation.
- Founder dashboard with decision distribution and estimated financial impact.
- Decision log and AI usage documentation.

## Technology Stack

- Python
- pandas
- Google Gemini API (`google-genai`)
- python-dotenv
- HTML and CSS
- JSON configuration
- CSV data storage

## Project Structure

```text
cod-rto-decision-system/
│
├── analysis/
│   ├── cleaned_orders.csv
│   ├── decision_log.csv
│   ├── financial_impact.csv
│   └── impact_simulation.csv
│
├── config/
│   └── rules.json
│
├── data/
│   └── orders_sample.csv
│
├── analyze_orders.py
├── decision_engine.py
├── run_decisions.py
├── financial_impact.py
├── simulate_impact.py
├── whatsapp_simulator.py
├── llm_validator.py
├── dashboard.py
├── dashboard.html
├── test_gemini.py
│
├── Business_Memo.docx
├── DECISION_LOG.md
├── AI_USAGE_LOG.md
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd cod-rto-decision-system


### Dataset Setup

The original customer-level dataset is excluded from this repository for privacy.

Place your authorized, anonymized assignment dataset at:

data/orders_sample.csv

Then run the analysis scripts.

The repository does not contain customer names, phone numbers, or delivery addresses.

```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_working_model_name
USE_LLM=true
USE_LLM_FOR_SAMPLE_TESTS=false
```

Do not commit `.env` or expose your API key publicly.

The application includes local validation as a fallback when Gemini is unavailable.

## How to Run

Run these commands from the project root.

### Step 1: Analyze historical orders

```bash
python analyze_orders.py
```

This cleans the dataset, removes exact duplicate records and generates analysis files for customer history, city, courier, marketing source and address length.

### Step 2: Generate order decisions

```bash
python run_decisions.py
```

This processes historical orders and creates:

`analysis/decision_log.csv`

### Step 3: Calculate historical financial baseline

```bash
python financial_impact.py
```

This calculates estimated RTO costs and contribution from delivered orders using the assignment assumptions.

### Step 4: Simulate financial impact

```bash
python simulate_impact.py
```

This estimates potential RTO savings, lost contribution and prepaid discount costs using configurable scenario assumptions.

### Step 5: Test WhatsApp responses

```bash
python whatsapp_simulator.py
```

The simulator supports YES, NO, PREPAID, random replies and no-response timeout scenarios.

### Step 6: Generate the founder dashboard

```bash
python dashboard.py
```

Open `dashboard.html` in a browser to view the decision distribution and estimated financial impact.

### Optional: Test Gemini connectivity

```bash
python test_gemini.py
```

This checks whether the configured Gemini API key and model can connect successfully.

## Decision Categories

| Action                | Meaning                                             |
| --------------------- | --------------------------------------------------- |
| SHIP_AS_IS            | No configured rule requires additional verification |
| WHATSAPP_CONFIRMATION | Confirm customer intent or delivery details         |
| NUDGE_TO_PREPAID      | Offer an optional prepaid discount                  |
| HOLD_CANCEL_REVIEW    | Hold the order for manual review                    |

## Configurable Rules

Decision thresholds are stored in:

`config/rules.json`

The configuration includes:

- Maximum short-address length.
- Previous RTO threshold.
- WhatsApp confirmation timeout.
- Reminder limit.
- Prepaid discount percentage.
- Minimum order value for prepaid offers.
- Actions for configured risk conditions.

Operations users can adjust supported thresholds without editing the Python decision logic.

## Historical Analysis Results

The supplied dataset contained 2,018 rows. After removing 30 exact duplicate rows, 1,988 records remained.

Of these, 1,987 had known final outcomes:

- Delivered: 1,422
- RTO: 565
- Historical RTO rate: 28.43%

The analysis identified higher observed RTO rates among customers with previous RTO history and orders with very short addresses.

## Financial Assumptions

Estimated cost per RTO:

- Forward shipping: ₹65
- Return shipping: ₹65
- Packaging and handling: ₹25
- Expected damage cost: 8% × ₹180 = ₹14.40

**Estimated total cost per RTO: ₹169.40**

The financial impact simulation estimates a net impact of ₹24,704.55 under its stated assumptions.

This is a hypothetical scenario estimate, not measured or guaranteed savings. Actual results require a controlled pilot.

## AI and Decision-Making Approach

The system separates tasks between deterministic code and AI:

- Python handles numerical thresholds, order decisions and financial calculations.
- Gemini is intended for ambiguous customer names and address interpretation.
- Local validation provides a fallback when the Gemini API is unavailable.

The historical batch decision run used local fallback validation. Gemini connectivity was tested separately; the historical dataset was not batch-processed using Gemini.

See `AI_USAGE_LOG.md` for details.

## Documentation

- `Business_Memo.docx` – Business recommendations and financial trade-offs.
- `DECISION_LOG.md` – Major implementation decisions and alternatives.
- `AI_USAGE_LOG.md` – AI tools, limitations and corrections.

## Limitations

- The supplied dataset is historical sample data, not a live Shopify feed.
- The dashboard displays historical sample results, not actual yesterday's live orders.
- WhatsApp is simulated; no real messages are sent.
- Financial benefits depend on assumptions that require pilot validation.
- Manual review is recommended before cancelling potentially genuine customer orders.

## Future Improvements

- Integrate Shopify order webhooks.
- Integrate the WhatsApp Business API.
- Add live order monitoring.
- Validate AI address classification with human-reviewed examples.
- Run controlled experiments to measure actual RTO reduction.
- Add courier and regional performance monitoring.

## Author

Developed as part of the Associate Software Engineer – AI Automation Engineer Take-Home Assignment.
