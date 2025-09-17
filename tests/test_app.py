from __future__ import annotations

from math import isclose

import numpy as np
import pandas as pd
import pytest

from mortgage_tools.app import (
    CurrentLoan,
    RefiOffer,
    amortization_schedule,
    break_even_months,
    build_savings_stream,
    compute_ltv,
    effective_refi_costs,
    npv_of_refi,
    payment,
    remaining_balance,
    total_interest_from_schedule,
)


# --------------------------------- Fixtures --------------------------------- #
@pytest.fixture
def sample_loan_params() -> dict[str, float | int]:
    return {"principal": 300_000, "annual_rate_pct": 6.0, "years": 30}


@pytest.fixture
def zero_rate_loan_params() -> dict[str, float | int]:
    return {"principal": 300_000, "annual_rate_pct": 0.0, "years": 30}


@pytest.fixture
def sample_current_loan() -> CurrentLoan:
    return CurrentLoan(
        original_principal=400_000,
        apr_pct=6.75,
        original_term_years=30,
        payments_made=36,
        monthly_pmi=100.0,
    )


@pytest.fixture
def sample_refi_offer() -> RefiOffer:
    return RefiOffer(
        new_principal=380_000,
        apr_pct=5.5,
        term_years=25,
        points_pct_of_loan=0.5,
        lender_credits=500.0,
        other_closing_costs=2000.0,
        monthly_pmi=50.0,
    )


# -------------------------------- Core Math Tests ------------------------------- #
def test_payment(sample_loan_params):
    pmt = payment(**sample_loan_params)
    assert isclose(pmt, 1798.65, abs_tol=0.01)


def test_payment_zero_rate(zero_rate_loan_params):
    pmt = payment(**zero_rate_loan_params)
    assert isclose(pmt, 300_000 / 360, abs_tol=0.01)


def test_payment_zero_term():
    pmt = payment(principal=100_000, annual_rate_pct=5.0, years=0)
    assert isclose(pmt, 100_000)


def test_remaining_balance(sample_loan_params):
    balance = remaining_balance(
        original_principal=sample_loan_params["principal"],
        annual_rate_pct=sample_loan_params["annual_rate_pct"],
        years_total=sample_loan_params["years"],
        payments_made=60,
    )
    assert isclose(balance, 279_163.07, abs_tol=0.01)


def test_remaining_balance_zero_rate(zero_rate_loan_params):
    balance = remaining_balance(
        original_principal=zero_rate_loan_params["principal"],
        annual_rate_pct=zero_rate_loan_params["annual_rate_pct"],
        years_total=zero_rate_loan_params["years"],
        payments_made=60,
    )
    expected_balance = (
        zero_rate_loan_params["principal"]
        - (zero_rate_loan_params["principal"] / 360) * 60
    )
    assert isclose(balance, expected_balance, abs_tol=0.01)


def test_remaining_balance_full_term(sample_loan_params):
    balance = remaining_balance(
        original_principal=sample_loan_params["principal"],
        annual_rate_pct=sample_loan_params["annual_rate_pct"],
        years_total=sample_loan_params["years"],
        payments_made=360,
    )
    assert isclose(balance, 0.0, abs_tol=1.0)  # Allow small tolerance


def test_amortization_schedule(sample_loan_params):
    df = amortization_schedule(**sample_loan_params)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 360
    assert isclose(df["balance"].iloc[-1], 0.0, abs_tol=1.0)
    assert isclose(df["interest"].sum(), 347_514.78, abs_tol=1.0)


def test_amortization_schedule_with_extra_payments(sample_loan_params):
    df = amortization_schedule(**sample_loan_params, extra_principal_per_period=200)
    assert df.shape[0] < 360
    assert isclose(df["balance"].iloc[-1], 0.0, abs_tol=1.0)
    assert df["interest"].sum() < 347_514.78


def test_total_interest_from_schedule(sample_loan_params):
    df = amortization_schedule(**sample_loan_params)
    total_interest = total_interest_from_schedule(df)
    assert isclose(total_interest, df["interest"].sum())


def test_break_even_months():
    result = break_even_months(5000, 200)
    assert result is not None
    assert isclose(result, 25)
    assert break_even_months(5000, 0) is None
    assert break_even_months(5000, -100) is None


def test_npv_of_refi():
    savings = np.array([100] * 120)  # 10 years of $100/mo savings
    npv = npv_of_refi(
        monthly_savings_stream=savings,
        monthly_discount_rate=0.05 / 12,
        upfront_costs=5000,
    )
    # PV of annuity formula for verification: 100 * (1 - (1 + 0.05/12)^-120) / (0.05/12)
    expected_pv_savings = 9428.14
    assert isclose(npv, expected_pv_savings - 5000, abs_tol=0.01)


# ----------------------------- Helper Function Tests ---------------------------- #
def test_effective_refi_costs(sample_refi_offer):
    costs = effective_refi_costs(sample_refi_offer)
    expected_points = 0.005 * 380_000
    expected_costs = expected_points - 500 + 2000
    assert isclose(costs, expected_costs)


def test_compute_ltv():
    assert isclose(compute_ltv(400_000, 500_000), 0.8)
    assert compute_ltv(400_000, 0) == float("inf")


def test_build_savings_stream():
    cur_sched = pd.DataFrame({"payment": [1000] * 24})
    new_sched = pd.DataFrame({"payment": [800] * 36})
    stream = build_savings_stream(
        cur_sched=cur_sched,
        new_sched=new_sched,
        months=30,
        cur_pmi=50,
        new_pmi=25,
    )
    assert stream.shape == (30,)
    # First 24 months: (1000+50) - (800+25) = 225
    assert np.all(stream[:24] == 225)
    # Next 6 months: (0+50) - (800+25) = -775
    assert np.all(stream[24:] == -775)


def test_build_savings_stream_new_shorter():
    """Test savings stream when the new loan is shorter than the horizon."""
    cur_sched = pd.DataFrame({"payment": [1000] * 36, "interest": [100] * 36})
    new_sched = pd.DataFrame({"payment": [800] * 24, "interest": [80] * 24})
    stream = build_savings_stream(
        cur_sched=cur_sched,
        new_sched=new_sched,
        months=30,
        cur_pmi=50,
        new_pmi=25,
    )
    assert stream.shape == (30,)
    # First 24 months: (1000+50) - (800+25) = 225
    assert np.all(stream[:24] == 225)
    # Next 6 months: (1000+50) - (0+25) = 1025
    assert np.all(stream[24:] == 1025)
