
import math
import pandas as pd

def pmt(rate_m, n_periods, principal):
    """Monthly annuity payment (positive) for principal at rate_m over n_periods."""
    if principal <= 0:
        return 0.0
    if rate_m == 0:
        return principal / n_periods
    return principal * (rate_m * (1 + rate_m) ** n_periods) / ((1 + rate_m) ** n_periods - 1)

def amortization_schedule(principal, annual_rate, years, insurance_rate_annual=0.0, start_month=1, start_year=2025):
    """Return a DataFrame with monthly amortization including optional borrower insurance (linear on principal)."""
    months = int(years * 12)
    rate_m = annual_rate / 12.0
    ins_m = insurance_rate_annual / 12.0
    annuity = pmt(rate_m, months, principal)
    rows = []
    balance = principal
    y, m = start_year, start_month
    for i in range(1, months + 1):
        interest = balance * rate_m
        principal_paid = annuity - interest
        balance = max(0.0, balance - principal_paid)
        insurance = principal * ins_m
        total = annuity + insurance
        rows.append({
            "period": i,
            "year": y, "month": m,
            "payment_annuity": annuity,
            "interest": interest,
            "principal_paid": principal_paid,
            "insurance": insurance,
            "payment_total": total,
            "balance": balance
        })
        m += 1
        if m > 12:
            m = 1; y += 1
    df = pd.DataFrame(rows)
    return df

def scenario_monthly_payment(principal, rate_annual, years, insurance_rate_annual=0.0):
    """Return (annuity, insurance_monthly, total) for a scenario."""
    months = int(years * 12)
    rate_m = rate_annual / 12.0
    annuity = pmt(rate_m, months, principal)
    insurance_m = principal * (insurance_rate_annual / 12.0)
    total = annuity + insurance_m
    return annuity, insurance_m, total

def build_financing_table(principal, rates_by_years, insurance_rate_annual=0.0, stress_bp=[0, 50, 100]):
    """Create a table of monthly payments for multiple durations and stressed rates in basis points (+bp)."""
    rows = []
    for years, base_rate in rates_by_years.items():
        for bp in stress_bp:
            rate = base_rate + bp / 10000.0
            ann, ins, tot = scenario_monthly_payment(principal, rate, years, insurance_rate_annual)
            rows.append({
                "duration_years": years,
                "rate_%": round(rate * 100, 3),
                "annuity": ann,
                "insurance": ins,
                "monthly_payment_total": tot,
                "stress_bp": bp
            })
    return pd.DataFrame(rows).sort_values(["duration_years", "stress_bp"])
