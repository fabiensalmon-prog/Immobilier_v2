
import streamlit as st
import pandas as pd
from core.finance import build_financing_table, amortization_schedule

st.header("💶 Financement – Taux & mensualités")

params = st.session_state.get("params", None)
if params is None:
    st.warning("Allez dans **Paramètres** pour initialiser taux, durée et assurance.")
    st.stop()

st.markdown("Chargez un **tableau de taux** (CSV) ou utilisez les taux par défaut 2025‑08 (Observatoire CL/CSA).")

rates_file = st.file_uploader("📥 Taux par durée (CSV) – colonnes: duration_years, rate_percent, source", type=["csv"])

if rates_file is not None:
    rates_df = pd.read_csv(rates_file)
else:
    rates_df = pd.read_csv("data/examples/rates_2025-08.csv")

st.write(rates_df)

# Pick a principal to finance
principal = st.number_input("Montant à financer (€)", min_value=0, value=250000, step=5000)
insurance = st.slider("Assurance emprunteur annuelle (% du capital)", 0.0, 1.0, float(params.get("assurance", 0.003)*100.0), 0.01) / 100.0

# Build table
rates_by_years = {int(r["duration_years"]): float(r["rate_percent"]) / 100.0 for _, r in rates_df.iterrows()}
stress = st.multiselect("Stress (bp)", [0, 50, 100, 150, 200], default=[0, 100])
table = build_financing_table(principal, rates_by_years, insurance_rate_annual=insurance, stress_bp=stress)

st.subheader("📋 Tableau de mensualités (avec stress)")
st.dataframe(
    table.style.format({
        "rate_%": "{:.2f}%".format,
        "annuity": "€{:,.0f}".format,
        "insurance": "€{:,.0f}".format,
        "monthly_payment_total": "€{:,.0f}".format
    }),
    use_container_width=True
)

# Amortization detail for a chosen scenario
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    years = st.selectbox("Durée (ans)", sorted(rates_by_years.keys()), index=sorted(rates_by_years.keys()).index(25) if 25 in rates_by_years else 0)
with col2:
    rate = st.number_input("Taux annuel (%)", value=float(rates_by_years[years] * 100), step=0.01)
df_amort = amortization_schedule(principal, annual_rate=rate/100.0, years=years, insurance_rate_annual=insurance)
st.subheader("📆 Amortissement (extrait 24 mois)")
st.dataframe(
    df_amort.head(24).style.format({
        "payment_annuity": "€{:,.0f}".format,
        "interest": "€{:,.0f}".format,
        "principal_paid": "€{:,.0f}".format,
        "insurance": "€{:,.0f}".format,
        "payment_total": "€{:,.0f}".format,
        "balance": "€{:,.0f}".format
    }),
    use_container_width=True
)
