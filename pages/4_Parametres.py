
import streamlit as st
import pandas as pd

st.header("⚙️ Paramètres & hypothèses (globaux)")

if "params" not in st.session_state:
    st.session_state["params"] = {}
p = st.session_state["params"]

st.subheader("Stratégie locative")
p["strategy"] = st.selectbox("Type", ["meuble", "nu", "colocation"], index=0)

st.subheader("Encadrement des loyers")
p["apply_cap"] = st.checkbox("Appliquer un plafond €/m² (loyer de référence majoré)", value=True)
p["cap_per_m2"] = st.number_input("Plafond €/m²", min_value=0.0, value=0.0, step=0.5)
p["rent_control_cities"] = {c.lower() for c in ["Paris","Lille","Lyon","Villeurbanne","Montpellier","Bordeaux"]}

st.subheader("Financement (par défaut pour le scoring)")
p["taux"] = st.slider("Taux nominal annuel (%)", 1.0, 6.0, 3.05, 0.01) / 100.0
p["assurance"] = st.slider("Assurance annuelle (% du capital)", 0.0, 1.0, 0.30, 0.01) / 100.0
p["duree_annees"] = st.slider("Durée (années)", 10, 30, 25, 1)

st.subheader("Frais d'acquisition")
p["frais_notaires"] = st.slider("Frais de notaire (% du prix)", 6.0, 9.0, 7.5, 0.1) / 100.0
p["travaux"] = st.number_input("Travaux (EUR)", min_value=0, value=0, step=1000)
p["apport"] = st.number_input("Apport (EUR)", min_value=0, value=0, step=1000)

st.subheader("Charges récurrentes (mensuelles ou % du loyer)")
p["vacancy_rate"] = st.slider("Vacance (% loyer)", 0.0, 15.0, 8.0, 0.5) / 100.0
p["mgmt_rate"] = st.slider("Gestion locative (% loyer)", 0.0, 12.0, 7.0, 0.5) / 100.0
p["nonrecup_rate"] = st.slider("Charges non récupérables (% loyer)", 0.0, 12.0, 5.0, 0.5) / 100.0
p["capex_rate"] = st.slider("Capex/Entretien (% loyer)", 0.0, 12.0, 5.0, 0.5) / 100.0
p["gli_rate"] = st.slider("GLI (% loyer)", 0.0, 5.0, 2.5, 0.1) / 100.0
p["pno_monthly"] = st.number_input("PNO (€/mois)", min_value=0.0, value=12.0, step=1.0)
p["taxe_fonciere_monthly"] = st.number_input("Taxe foncière (€/mois)", min_value=0.0, value=0.0, step=10.0)
p["compta_monthly"] = st.number_input("Comptable/Expert LMNP (€/mois)", min_value=0.0, value=0.0, step=5.0)

st.subheader("Villes ciblées & barème €/m² (fallback éditable)")
st.caption("Charge un CSV barème dans le Dashboard pour écraser ces valeurs. Ici tu peux **éditer** les €/m² par ville si tu n'as pas de fichier.")
if "rpm2_table" not in p:
    p["rpm2_table"] = pd.DataFrame({"city": ["Brest","Paris"], "rent_per_m2":[9.5, 30.0]})
editable = st.data_editor(p["rpm2_table"], num_rows="dynamic", use_container_width=True)
# Store as dict fallback (lowercase keys)
p["rpm2_fallback"] = {"default": float(editable["rent_per_m2"].mean() if not editable.empty else 20.0)}
for _, r in editable.iterrows():
    p["rpm2_fallback"][str(r["city"]).lower()] = float(r["rent_per_m2"])

st.success("✅ Paramètres mis à jour. Ouvrez **Dashboard** et **Financement**.")
