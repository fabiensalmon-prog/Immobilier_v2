
import streamlit as st
import pandas as pd
from core.finance import build_financing_table
from core.scoring import compute_scores
from core.rents import estimate_rent_per_m2, apply_rent_cap
from core.dvf import load_dvf_medians, price_gap_vs_dvf

st.set_page_config(page_title="Ultimate Invest – Immobilier locatif", layout="wide")

st.title("🏠 Ultimate Invest – Immobilier locatif")
st.caption("Version 'investisseur pro' : scoring multi-stratégies, stress tests, DVF, financement, encadrement des loyers.")

st.markdown("""
**Comment utiliser :**
1) Allez dans **Paramètres** pour régler vos charges (GLI, PNO, TF...) et votre **stratégie** (nu, meublé, colocation).  
2) Chargez vos **annonces** + **barème loyers** + (optionnel) **médians DVF**.  
3) Explorez **Dashboard** (Top opportunités) et **Financement** (tableau de mensualités avec taux à jour et stress).  
4) La **Carte** met en évidence les zones et les biens à fort score.
""")

st.info("💡 Astuce : dans *Paramètres*, vous trouverez un **plafond €/m²** pour gérer l'encadrement des loyers (Paris, Lille, Lyon/Villeurbanne, Montpellier, Bordeaux, etc.).")

st.markdown("---")
st.subheader("📦 Fichiers d'exemple")
st.write("Téléchargez ces CSV pour tester :")
from pathlib import Path
example_dir = Path("data/examples")
for fn in ["listings_example.csv", "rents_example.csv", "dvf_medians_example.csv", "rates_2025-08.csv"]:
    with open(example_dir / fn, "rb") as f:
        st.download_button(f"⬇️ {fn}", data=f.read(), file_name=fn)
