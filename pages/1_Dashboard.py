
import streamlit as st
import pandas as pd
import numpy as np
from core.scoring import compute_scores
from core.dvf import load_dvf_medians, price_gap_vs_dvf

st.header("📊 Dashboard – Top opportunités par ville")
params = st.session_state.get("params", None)
if params is None:
    st.warning("Allez dans **Paramètres** pour définir vos hypothèses (taux, charges, plafond €/m²...).")
    st.stop()

uploaded = st.file_uploader("📥 Annonces (CSV)", type=["csv"], key="listings")
bench = st.file_uploader("📥 Barème loyers (CSV, optionnel)", type=["csv"], key="bench")
dvf = st.file_uploader("📥 DVF – Médians prix/m² (CSV optionnel)", type=["csv"], key="dvf")

rent_bench_df = None
dvf_df = None

if bench is not None:
    rent_bench_df = pd.read_csv(bench)
    params["rent_bench_df"] = rent_bench_df
else:
    params["rent_bench_df"] = None  # rely on fallback editable table

if dvf is not None:
    dvf_df = load_dvf_medians(pd.read_csv(dvf))

if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.write(f"Annonces chargées : **{df.shape[0]}** lignes")

    # City picker based on data
    cols = {c.lower(): c for c in df.columns}
    city_col = cols.get("city") or cols.get("ville")
    if not city_col:
        st.error("Le CSV doit contenir une colonne 'city' (ou 'ville').")
        st.stop()
    cities = sorted(df[city_col].dropna().astype(str).unique().tolist())
    selected_city = st.selectbox("Ville", options=cities, index=0)

    # Filter by city
    df_city = df[df[city_col].astype(str) == selected_city].copy()

    try:
        results = compute_scores(df_city, params, strategy=params.get("strategy", "meuble"))
        # DVF gap (optional)
        if dvf_df is not None:
            price_col = cols.get("price") or cols.get("prix")
            surf_col  = cols.get("surface_m2") or cols.get("surface") or cols.get("surface_m²")
            gaps = []
            for i, row in results.iterrows():
                gaps.append(price_gap_vs_dvf(price=row[price_col], surface_m2=row[surf_col], city=selected_city, dvf_df=dvf_df))
            results["price_gap_vs_dvf_%"] = gaps

        # Auto-filter rentable (cashflow >= 0)
        st.checkbox("Ne montrer que les biens rentables (cashflow ≥ 0 €/mois)", value=True, key="only_rentable")
        filt = results.copy()
        if st.session_state["only_rentable"]:
            filt = filt[filt["cashflow_monthly"] >= 0]

        # Thresholds
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            net_yield_min = st.number_input("Rendement net min (%)", value=0.0, step=0.1)
        with col2:
            score_min = st.number_input("Score investisseur min (/100)", value=0, step=5)
        with col3:
            topn = st.number_input("Top N", min_value=1, value=min(20, len(filt)), step=1)
        with col4:
            sort_key = st.selectbox("Trier par", ["cashflow_monthly","investor_score","net_yield_%","gross_yield_%"], index=0)
        filt = filt[(filt["net_yield_%"].fillna(0) >= net_yield_min) & (filt["investor_score"].fillna(0) >= score_min)]
        filt = filt.sort_values(sort_key, ascending=False)

        st.subheader(f"🏆 Opportunités – {selected_city}")
        st.dataframe(
            filt.head(int(topn)).style.format({
                "expected_price": "€{:,.0f}".format,
                "rent_est_monthly": "€{:,.0f}".format,
                "net_rent_monthly": "€{:,.0f}".format,
                "monthly_payment": "€{:,.0f}".format,
                "insurance_monthly": "€{:,.0f}".format,
                "cashflow_monthly": "€{:,.0f}".format,
                "gross_yield_%": "{:.2f}%".format,
                "net_yield_%": "{:.2f}%".format,
                "coc_%": "{:.2f}%".format,
                "investor_score": "{:.1f}".format,
                "price_gap_vs_dvf_%": "{:.1f}%".format
            }, na_rep="—"),
            use_container_width=True
        )

        # ---- Property detail panel ----
        st.markdown("---")
        st.subheader("🔎 Détail du bien sélectionné")
        # Build a selector: try using an 'id' or 'url' or row index
        key_cols = [c for c in ["id","url","title"] if c in filt.columns]
        label_col = key_cols[0] if key_cols else filt.columns[0]
        options = filt.index.tolist()
        def labeler(idx):
            row = filt.loc[idx]
            lab = str(row[label_col]) if label_col in filt.columns else f"Bien #{idx}"
            cf = row["cashflow_monthly"]
            return f"{lab}  —  CF: €{cf:,.0f}/mois"
        selected_idx = st.selectbox("Choisis un bien", options=options, format_func=labeler)

        if selected_idx is not None:
            row = filt.loc[selected_idx]
            price_col = cols.get("price") or cols.get("prix")
            surf_col  = cols.get("surface_m2") or cols.get("surface") or cols.get("surface_m²")
            dom_col   = cols.get("days_on_market") or cols.get("dom") or cols.get("jours_en_ligne")
            url_col   = cols.get("url") or cols.get("lien")

            colA, colB, colC = st.columns(3)
            with colA:
                st.metric("Prix affiché", f"€{row[price_col]:,.0f}")
                if dom_col and dom_col in row.index:
                    st.metric("Ancienneté annonce (jours)", f"{int(row[dom_col])}")
                if url_col and url_col in row.index and not pd.isna(row[url_col]):
                    st.write(f"[Voir l'annonce]({row[url_col]})")
            with colB:
                st.metric("Prix négocié (attendu)", f"€{row['expected_price']:,.0f}")
                st.metric("Mensualité + assurance", f"€{(row['monthly_payment']+row['insurance_monthly']):,.0f}/mois")
            with colC:
                st.metric("Loyer estimé (brut)", f"€{row['rent_est_monthly']:,.0f}/mois")
                st.metric("Cashflow (net)", f"€{row['cashflow_monthly']:,.0f}/mois")

            with st.expander("🧾 Décomposition cashflow (mensuel)"):
                breakdown = pd.DataFrame({
                    "poste": ["Loyer estimé (brut)","Loyer net après vacance/gestion/charges/CapEx/GLI","Mensualité (hors assur.)","Assurance empr.","Cashflow net"],
                    "€ / mois": [
                        row["rent_est_monthly"],
                        row["net_rent_monthly"],
                        row["monthly_payment"],
                        row["insurance_monthly"],
                        row["cashflow_monthly"],
                    ]
                })
                st.dataframe(breakdown.style.format({"€ / mois": "€{:,.0f}".format}), hide_index=True, use_container_width=True)

            if "price_gap_vs_dvf_%" in filt.columns and not pd.isna(row.get("price_gap_vs_dvf_%", np.nan)):
                gap = row["price_gap_vs_dvf_%"]
                st.info(f"Écart prix/m² vs DVF (ville): {gap:+.1f} %")

    except Exception as e:
        st.error(f"Erreur de calcul: {e}")
else:
    st.info("Importez vos **annonces**. Optionnel : **barème loyers** et **DVF**.")
