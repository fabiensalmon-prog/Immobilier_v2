
import numpy as np
import pandas as pd
from .rents import estimate_rent_per_m2, apply_rent_cap

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def monthly_net_rent(gross_monthly_rent, vacancy_rate, mgmt_rate, nonrecup_rate, capex_rate, gli_rate, pno_monthly, tf_monthly, compta_monthly):
    """Deduct % on rent (vacancy, mgmt, nonrecup, capex, GLI) + fixed (PNO, TF, Comptabilité)"""
    deductions_pct = clamp(vacancy_rate + mgmt_rate + nonrecup_rate + capex_rate + gli_rate, 0.0, 0.95)
    return gross_monthly_rent * (1 - deductions_pct) - (pno_monthly + tf_monthly + compta_monthly)

def compute_scores(df, params, strategy="meuble"):
    df = df.copy()
    cols = {c.lower(): c for c in df.columns}
    price_col = cols.get("price") or cols.get("prix")
    surf_col  = cols.get("surface_m2") or cols.get("surface") or cols.get("surface_m²")
    city_col  = cols.get("city") or cols.get("ville")
    type_col  = cols.get("property_type") or cols.get("type")
    dom_col   = cols.get("days_on_market") or cols.get("dom") or cols.get("jours_en_ligne")
    url_col   = cols.get("url") or cols.get("lien")

    required = [price_col, surf_col, city_col]
    if any(c is None for c in required):
        raise ValueError("CSV annonces: colonnes minimales requises = price, surface_m2, city")

    # Negotiation
    base_neg = params["base_neg"]
    extra_per_30d = params["extra_per_30d"]
    neg_max = params["neg_max"]
    if dom_col and df[dom_col].notna().any():
        extra = (df[dom_col].fillna(0).astype(float) / 30.0) * extra_per_30d
    else:
        extra = 0.0
    neg_rate = (base_neg + extra).clip(0, neg_max)
    df["expected_price"] = df[price_col].astype(float) * (1 - neg_rate)

    # Acquisition costs
    df["notary_fees"] = df["expected_price"] * params["frais_notaires"]
    df["travaux"] = params["travaux"]
    df["apport"] = params["apport"]

    # Financing
    df["to_finance"] = (df["expected_price"] + df["notary_fees"] + df["travaux"] - df["apport"]).clip(lower=0)
    # Monthly payments: use selected duration and rate
    years = params["duree_annees"]
    rate_m = params["taux"] / 12.0
    def pmt(rate_m, n, p):
        if p <= 0: return 0.0
        if rate_m == 0: return p / n
        return p * (rate_m * (1 + rate_m) ** n) / ((1 + rate_m) ** n - 1)

    n_months = int(years * 12)
    df["monthly_payment"] = df["to_finance"].apply(lambda p: pmt(rate_m, n_months, p))
    df["insurance_monthly"] = df["to_finance"] * (params["assurance"] / 12.0)

    # Rent estimation + strategy uplift
    rpm2_fallback = params["rpm2_fallback"]
    rent_bench_df = params.get("rent_bench_df")
    apply_cap_flag = params["apply_cap"]
    cap_per_m2 = params["cap_per_m2"]
    encadrement_cities = params["rent_control_cities"]

    def strat_multiplier(pt):
        s = strategy.lower()
        if s == "nu": return 1.00
        if s == "meuble": return 1.10  # +10% typiquement
        if s == "colocation": return 1.40  # +40% (à affiner selon marché)
        return 1.00

    def row_rent(row):
        city = str(row[city_col]); pt = str(row[type_col]) if type_col else "all"
        rpm2 = estimate_rent_per_m2(city, pt, rent_bench_df, rpm2_fallback)
        est = float(row[surf_col]) * rpm2 * strat_multiplier(pt)
        capped = apply_rent_cap(est, float(row[surf_col]), cap_per_m2, apply_cap_flag and city.lower() in encadrement_cities)
        return capped

    df["rent_est_monthly"] = df.apply(row_rent, axis=1)

    # Operating net rent (deductions + fixed)
    vacancy_rate = params["vacancy_rate"]; mgmt_rate = params["mgmt_rate"]
    nonrecup_rate = params["nonrecup_rate"]; capex_rate = params["capex_rate"]
    gli_rate = params["gli_rate"]; pno_monthly = params["pno_monthly"]; tf_monthly = params["taxe_fonciere_monthly"]; compta_monthly = params["compta_monthly"]

    df["net_rent_monthly"] = df["rent_est_monthly"].apply(lambda r: monthly_net_rent(r, vacancy_rate, mgmt_rate, nonrecup_rate, capex_rate, gli_rate, pno_monthly, tf_monthly, compta_monthly))

    # Cashflow
    df["cashflow_monthly"] = df["net_rent_monthly"] - df["monthly_payment"] - df["insurance_monthly"]

    # Yields
    df["gross_yield_%"] = (df["rent_est_monthly"] * 12.0) / df["expected_price"] * 100.0
    denom_net = (df["expected_price"] + df["notary_fees"] + df["travaux"]).replace(0, np.nan)
    df["net_yield_%"] = ((df["net_rent_monthly"] - df["insurance_monthly"]) * 12.0) / denom_net * 100.0

    # Cash-on-cash
    cash_in = (df["apport"] + df["notary_fees"] + df["travaux"]).replace(0, np.nan)
    df["coc_%"] = (df["cashflow_monthly"] * 12.0) / cash_in * 100.0

    # Normalize features for score
    def normalize(series):
        s = series.replace([np.inf, -np.inf], np.nan).dropna()
        if s.empty or s.max() == s.min():
            return pd.Series([0.5] * len(series), index=series.index)
        return (series - s.min()) / (s.max() - s.min())

    norm_cf = normalize(df["cashflow_monthly"])
    norm_net_yield = normalize(df["net_yield_%"])
    norm_dom = normalize(df[dom_col]) if dom_col in df.columns else pd.Series([0.5] * len(df), index=df.index)

    df["investor_score"] = (0.40 * norm_cf) + (0.25 * norm_net_yield) + (0.15 * (1 - norm_dom)) + (0.20 * normalize(df["gross_yield_%"]))
    df["investor_score"] = df["investor_score"].fillna(0) * 100.0

    # Sort
    df = df.sort_values(["cashflow_monthly", "investor_score"], ascending=[False, False])

    # Final columns
    out_cols = [
        city_col, surf_col, price_col, "expected_price",
        "rent_est_monthly", "net_rent_monthly",
        "monthly_payment", "insurance_monthly",
        "cashflow_monthly", "gross_yield_%", "net_yield_%", "coc_%", "investor_score"
    ]
    if dom_col in df.columns:
        out_cols.insert(3, dom_col)
    if url_col in df.columns:
        out_cols.append(url_col)
    for c in out_cols:
        if c not in df.columns: # safety
            df[c] = None
    return df[out_cols]
