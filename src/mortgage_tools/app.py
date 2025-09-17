"""A Streamlit app for analyzing mortgage refinancing options."""

from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from math import isclose
from typing import Literal

import numpy as np
import pandas as pd
import streamlit as st

Period = Literal["monthly"]


# ------------------------------- Core Math --------------------------------- #
def payment(
    principal: float,
    annual_rate_pct: float,
    years: float,
    *,
    periods_per_year: int = 12,
) -> float:
    """Compute fixed-payment loan installment for fully amortizing loan.

    Args:
        principal: Loan amount (present value L).
        annual_rate_pct: Nominal APR as percent (e.g., 6.5 for 6.5%).
        years: Term in years (can be float).
        periods_per_year: Compounding/payment frequency (default 12).

    Returns:
        The level payment per period.

    Notes:
        Formula:
            P = r * L / (1 - (1 + r)^(-n))
        where r = APR / periods_per_year, n = years * periods_per_year.
    """
    n = years * periods_per_year
    if n == 0:
        return principal
    r = (annual_rate_pct / 100.0) / periods_per_year
    if isclose(r, 0.0):
        return principal / n
    return r * principal / (1.0 - (1.0 + r) ** (-n))


def remaining_balance(
    original_principal: float,
    annual_rate_pct: float,
    years_total: int,
    payments_made: int,
    *,
    periods_per_year: int = 12,
) -> float:
    """Compute remaining balance after k payments on an amortizing loan.

    Args:
        original_principal: Original loan amount at origination.
        annual_rate_pct: Nominal APR as percent.
        years_total: Original term in years.
        payments_made: Number of payments already made.
        periods_per_year: Payments per year (default 12).

    Returns:
        Remaining principal owed after `payments_made`.
    """
    r = (annual_rate_pct / 100.0) / periods_per_year
    pmt = payment(
        original_principal,
        annual_rate_pct,
        years_total,
        periods_per_year=periods_per_year,
    )
    if isclose(r, 0.0):
        return original_principal - pmt * payments_made
    return original_principal * (1 + r) ** payments_made - pmt * (
        ((1 + r) ** payments_made - 1) / r
    )


def amortization_schedule(
    principal: float,
    annual_rate_pct: float,
    years: float,
    *,
    periods_per_year: int = 12,
    extra_principal_per_period: float = 0.0,
) -> pd.DataFrame:
    """Generate an amortization schedule DataFrame.

    Args:
        principal: Starting principal.
        annual_rate_pct: APR in percent.
        years: Term in years (can be float).
        periods_per_year: Payments per year (default 12).
        extra_principal_per_period: Optional extra principal each period.

    Returns:
        DataFrame with columns:
            period, interest, principal, extra_principal, payment, balance.
    """
    r = (annual_rate_pct / 100.0) / periods_per_year
    base_pmt = payment(
        principal, annual_rate_pct, years, periods_per_year=periods_per_year
    )
    balance = principal
    rows: list[dict[str, float | int]] = []
    period = 0
    max_periods = round(years * periods_per_year)

    while balance > 0 and period < max_periods + 600:  # cap for extras
        period += 1
        interest = balance * r
        principal_component = base_pmt - interest
        extra = min(extra_principal_per_period, max(balance - principal_component, 0.0))
        principal_pay = min(principal_component + extra, balance)
        total_payment = interest + principal_pay
        balance = max(balance - principal_pay, 0.0)
        rows.append(
            {
                "period": period,
                "interest": float(interest),
                "principal": float(principal_component),
                "extra_principal": float(extra),
                "payment": float(total_payment),
                "balance": float(balance),
            }
        )
        if balance <= 0.0:
            break

    df = pd.DataFrame(rows)
    return df


def total_interest_from_schedule(df: pd.DataFrame) -> float:
    """Sum interest column from an amortization schedule DataFrame.

    Args:
        df: Amortization schedule with an 'interest' column.

    Returns:
        Total interest paid over schedule.
    """
    return float(df["interest"].sum())


def break_even_months(total_costs: float, monthly_savings: float) -> float | None:
    """Compute months to recover upfront refi costs via monthly savings.

    Args:
        total_costs: Upfront refinance costs (positive value).
        monthly_savings: Old P&I + PMI less new P&I + PMI (positive if saving).

    Returns:
        Months to break even, or None if monthly_savings <= 0.
    """
    if monthly_savings <= 0:
        return None
    return total_costs / monthly_savings


def npv_of_refi(
    monthly_savings_stream: np.ndarray,
    monthly_discount_rate: float,
    upfront_costs: float,
) -> float:
    """Compute NPV of refinancing given discounted savings stream.

    Args:
        monthly_savings_stream: Array of monthly savings over horizon.
        monthly_discount_rate: Monthly discount rate (e.g., 0.004 for ~5% APR).
        upfront_costs: Total upfront costs paid at t=0 (positive).

    Returns:
        Net present value of refinancing (positive = beneficial).
    """
    months = np.arange(1, monthly_savings_stream.size + 1)
    discount_factors = (1.0 + monthly_discount_rate) ** (-months)
    pv_savings = float(np.sum(monthly_savings_stream * discount_factors))
    return pv_savings - upfront_costs


# ------------------------------- Data Models -------------------------------- #
@dataclass(slots=True)
class CurrentLoan:
    """Describe the existing mortgage loan state."""

    original_principal: float
    apr_pct: float
    original_term_years: int
    payments_made: int
    monthly_pmi: float = 0.0


@dataclass(slots=True)
class RefiOffer:
    """Describe the proposed refinance loan offer."""

    new_principal: float
    apr_pct: float
    term_years: int
    points_pct_of_loan: float = 0.0
    lender_credits: float = 0.0
    other_closing_costs: float = 0.0
    monthly_pmi: float = 0.0
    extra_principal_per_month: float = 0.0


# ----------------------------- Helper Functions ----------------------------- #
def effective_refi_costs(offer: RefiOffer) -> float:
    """Compute effective upfront refi costs (points - credits + other costs).

    Args:
        offer: RefiOffer details.

    Returns:
        Upfront cost at time 0 (positive increases break-even time).
    """
    points_cost = offer.points_pct_of_loan / 100.0 * offer.new_principal
    return max(points_cost - offer.lender_credits, 0.0) + offer.other_closing_costs


def compute_ltv(principal_owed: float, home_value: float) -> float:
    """Compute loan-to-value ratio as a fraction (0..1)."""
    if home_value <= 0:
        return float("inf")
    return principal_owed / home_value


def build_savings_stream(
    cur_sched: pd.DataFrame,
    new_sched: pd.DataFrame,
    months: int,
    cur_pmi: float,
    new_pmi: float,
) -> np.ndarray:
    """Build monthly savings stream over horizon.

    Args:
        cur_sched: Current-loan schedule from month 1 onward.
        new_sched: New-loan schedule from month 1 onward.
        months: Planning horizon in months.
        cur_pmi: Monthly PMI for current loan (if any).
        new_pmi: Monthly PMI for new loan (if any).

    Returns:
        Array of (old P&I+PMI) - (new P&I+PMI) for each month up to horizon.
    """
    # Align lengths to horizon
    cur = cur_sched.head(months).copy()
    new = new_sched.head(months).copy()

    # If a schedule ends before the horizon, pad it with zeros
    if cur.shape[0] < months:
        pad_len = months - cur.shape[0]
        pad_df = pd.DataFrame(
            {col: [0.0] * pad_len for col in cur.columns},
            index=range(cur.shape[0], months),
        )
        cur = pd.concat([cur, pad_df])

    if new.shape[0] < months:
        pad_len = months - new.shape[0]
        pad_df = pd.DataFrame(
            {col: [0.0] * pad_len for col in new.columns},
            index=range(new.shape[0], months),
        )
        new = pd.concat([new, pad_df])

    cur_total = cur["payment"].to_numpy() + cur_pmi
    new_total = new["payment"].to_numpy() + new_pmi
    return cur_total - new_total


# --------------------------------- Streamlit -------------------------------- #
st.set_page_config(page_title="Refinance Analysis", page_icon="💸", layout="wide")
st.title("Mortgage Refinance Analyzer")

with st.sidebar:
    st.header("Current Loan")
    c_orig = st.number_input(
        "Original principal ($)", min_value=0.0, value=400_000.0, step=1_000.0
    )
    c_apr = st.number_input("Original APR (%)", min_value=0.0, value=6.75, step=0.05)
    c_term = st.number_input("Original term (years)", min_value=1, value=30, step=1)
    c_paid = st.number_input("Payments made (months)", min_value=0, value=36, step=1)
    c_pmi = st.number_input(
        "Current monthly PMI ($)", min_value=0.0, value=0.0, step=10.0
    )

    st.header("Home & Horizon")
    home_value = st.number_input(
        "Home value ($)", min_value=0.0, value=520_000.0, step=1_000.0
    )
    years_remaining_planning = st.slider(
        "How long do you expect to keep this mortgage (years)?", 1, 30, 7
    )
    discount_rate_pct = st.number_input(
        "Your discount rate (APR %) for NPV", min_value=0.0, value=5.0, step=0.25
    )

    st.header("Refi Offer")
    # Compute default new principal as current remaining balance
    cur_remaining = remaining_balance(
        c_orig, c_apr, c_term, c_paid, periods_per_year=12
    )
    r_principal = st.number_input(
        "New principal ($)",
        min_value=0.0,
        value=float(round(cur_remaining, 2)),
        step=1_000.0,
    )
    r_apr = st.number_input("New APR (%)", min_value=0.0, value=6.1, step=0.05)
    r_term = st.number_input(
        "New term (years)", min_value=1, value=max(c_term - c_paid // 12, 15), step=1
    )
    r_points = st.number_input(
        "Points (% of loan)", min_value=0.0, value=0.0, step=0.125
    )
    r_credits = st.number_input(
        "Lender credits ($)", min_value=0.0, value=0.0, step=100.0
    )
    r_other_costs = st.number_input(
        "Other closing costs ($)", min_value=0.0, value=4_000.0, step=100.0
    )
    r_pmi = st.number_input("New monthly PMI ($)", min_value=0.0, value=0.0, step=10.0)
    r_extra = st.number_input(
        "Extra principal per month on new loan ($)", min_value=0.0, value=0.0, step=50.0
    )

# Pack objects
current = CurrentLoan(
    original_principal=c_orig,
    apr_pct=c_apr,
    original_term_years=c_term,
    payments_made=c_paid,
    monthly_pmi=c_pmi,
)
refi = RefiOffer(
    new_principal=r_principal,
    apr_pct=r_apr,
    term_years=r_term,
    points_pct_of_loan=r_points,
    lender_credits=r_credits,
    other_closing_costs=r_other_costs,
    monthly_pmi=r_pmi,
    extra_principal_per_month=r_extra,
)

# Derived current state
remaining_principal = remaining_balance(
    current.original_principal,
    current.apr_pct,
    current.original_term_years,
    current.payments_made,
)
remaining_term_years = (current.original_term_years * 12 - current.payments_made) / 12.0
current_monthly_pmt = payment(
    remaining_principal,
    current.apr_pct,
    remaining_term_years,
)

# Schedules (from "now" forward)
cur_sched = amortization_schedule(
    principal=remaining_principal,
    annual_rate_pct=current.apr_pct,
    years=remaining_term_years,
    extra_principal_per_period=0.0,
)

new_sched = amortization_schedule(
    principal=refi.new_principal,
    annual_rate_pct=refi.apr_pct,
    years=refi.term_years,
    extra_principal_per_period=refi.extra_principal_per_month,
)

# Metrics
ltv_current = compute_ltv(remaining_principal, home_value)
ltv_new = compute_ltv(refi.new_principal, home_value)
upfront_costs = effective_refi_costs(refi)
months_horizon = years_remaining_planning * 12
monthly_discount_rate = (discount_rate_pct / 100.0) / 12.0

# Monthly payment comparison (P&I only)
new_monthly_pmt = payment(refi.new_principal, refi.apr_pct, refi.term_years)
monthly_savings_pi = (current_monthly_pmt) - (new_monthly_pmt)
monthly_savings_total = (current_monthly_pmt + current.monthly_pmi) - (
    new_monthly_pmt + refi.monthly_pmi
)

# Build savings stream over horizon using full schedules (P&I+PMI)
savings_stream = build_savings_stream(
    cur_sched=cur_sched,
    new_sched=new_sched,
    months=months_horizon,
    cur_pmi=current.monthly_pmi,
    new_pmi=refi.monthly_pmi,
)

npv = npv_of_refi(savings_stream, monthly_discount_rate, upfront_costs)
bem = break_even_months(upfront_costs, monthly_savings_total)

# Total interest (complete payoff perspective)
cur_total_interest = total_interest_from_schedule(cur_sched)
new_total_interest = total_interest_from_schedule(new_sched)
interest_saved_vs_full = cur_total_interest - new_total_interest

# Show results
c1, c2, c3, c4 = st.columns(4)
c1.metric("Current LTV", f"{ltv_current:0.1%}")
c2.metric("New LTV", f"{ltv_new:0.1%}")
c3.metric("Monthly P&I change", f"${monthly_savings_pi:,.0f}")
c4.metric("Monthly total change (incl. PMI)", f"${monthly_savings_total:,.0f}")

c5, c6, c7 = st.columns(3)
c5.metric("Upfront refi costs", f"${upfront_costs:,.0f}")
c6.metric(
    "Break-even (months)",
    "—" if bem is None else f"{bem:0.1f}",
    help="Months to recoup upfront costs from monthly savings.",
)
c7.metric(
    "NPV over horizon",
    f"${npv:,.0f}",
    help="Present value of savings over your horizon less upfront costs.",
)

st.subheader("Payments & Interest (from today forward)")
comp_df = pd.DataFrame(
    {
        "Current: Monthly P&I": [current_monthly_pmt],
        "New: Monthly P&I": [new_monthly_pmt],
        "Change (New - Current)": [new_monthly_pmt - current_monthly_pmt],
        "Total Interest Remaining (Current)": [cur_total_interest],
        "Total Interest (New Offer)": [new_total_interest],
        "Interest Saved (if held to payoff)": [interest_saved_vs_full],
    }
)
st.dataframe(comp_df, width="stretch")

st.subheader("Savings Over Your Horizon")
horizon_months = np.arange(1, months_horizon + 1)
horizon_df = pd.DataFrame(
    {"month": horizon_months, "cumulative_savings": savings_stream.cumsum()}
)
st.line_chart(horizon_df, x="month", y="cumulative_savings")

st.subheader("Amortization (first 24 rows shown)")
show_df = (
    cur_sched.add_prefix("cur_")
    .join(new_sched.add_prefix("new_"), how="outer", lsuffix="_c", rsuffix="_n")
    .fillna(0.0)
    .head(24)
)
st.dataframe(show_df, width="stretch")

# CSV export
st.subheader("Export Amortization Schedules")
csv_buf = StringIO()
full_export = (
    cur_sched.add_prefix("current_")
    .join(new_sched.add_prefix("new_"), how="outer")
    .fillna(0.0)
)
full_export.to_csv(csv_buf, index=False)
st.download_button(
    label="Download CSV (both schedules)",
    data=csv_buf.getvalue().encode("utf-8"),
    file_name="refinance_schedules.csv",
    mime="text/csv",
)

st.caption(
    "Notes: Payment calculations use standard level-payment amortization. "
    "PMI is modeled as a flat monthly amount you enter; in practice, PMI may "
    "drop when LTV ≤ 80% subject to lender/servicer rules."
)
