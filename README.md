# Mortgage Refinance Analyzer

A Streamlit web application designed to help homeowners analyze the financial implications of refinancing their mortgage. This tool provides a detailed comparison between a current mortgage and a refinancing offer, empowering users to make informed decisions with clear, actionable insights.

## Features

- **Side-by-Side Comparison**: Compares your current loan with a refinance offer, detailing changes in monthly payments (P&I), remaining interest, and total costs.
- **Key Financial Metrics**: Automatically calculates essential metrics, including:
  - **Loan-to-Value (LTV)**: For both current and new loans.
  - **Break-Even Point**: The number of months required to recoup the upfront costs of refinancing.
  - **Net Present Value (NPV)**: The total value of the refinance over a specified planning horizon, discounted to today's dollars.
- **Interactive Inputs**: A user-friendly sidebar allows for easy input of all relevant loan parameters, including principal, interest rates, term lengths, closing costs, and PMI.
- **Visual Analysis**:
  - A cumulative savings chart visualizes the financial benefit of refinancing over your chosen time horizon.
  - Amortization schedules for both loans are displayed and can be exported.
- **Data Export**: Download the complete amortization schedules for both the current and new loans as a single CSV file for offline analysis.

## Installation

This project uses `uv` for package management. To get started, you'll need to have Python 3.8+ and `uv` installed.

1. **Clone the repository:**

    ```bash
    git clone https://github.com/dvonpasecky/mortgage-tools.git
    cd mortgage-tools
    ```

2. **Create a virtual environment and install dependencies:**

    ```bash
    uv venv
    uv pip install -r requirements.txt
    ```

    *Note: On Windows, you may need to activate the environment first with `.venv\Scripts\activate`.*

## How to Run the Application

With the dependencies installed and the virtual environment activated, you can run the Streamlit app from the project root directory:

```bash
streamlit run src/mortgage_tools/app.py
```

This will start a local web server and open the application in your default browser.

## How It Works

The application is built on a foundation of standard financial formulas for mortgage amortization and investment analysis.

- **Payment Calculation**: Uses the level-payment formula to determine the fixed monthly principal and interest (P&I) for a fully amortizing loan.
- **Amortization Schedule**: Generates a month-by-month breakdown of interest and principal payments, showing how the loan balance decreases over time.
- **Break-Even Analysis**: Calculated by dividing the total upfront refinancing costs by the total monthly savings (including P&I and PMI). This determines how long it will take for the refinance to pay for itself.
- **Net Present Value (NPV)**: The core of the "is it worth it?" question. The NPV calculation discounts the future stream of monthly savings back to its value in today's dollars and subtracts the upfront refinancing costs. A positive NPV indicates that, from a purely financial standpoint, the refinance is a beneficial decision over your specified planning horizon.
