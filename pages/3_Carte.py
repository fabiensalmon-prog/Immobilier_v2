
import streamlit as st
import pandas as pd

st.header("🗺️ Carte (bêta)")
st.info("Pour garder l'app légère, la carte est optionnelle. Vous pouvez charger un CSV d'annonces géocodées (lat, lon) et afficher les scores (bientôt Folium).")

uploaded = st.file_uploader("📥 Annonces géocodées (CSV avec colonnes lat, lon, investor_score)", type=["csv"])
if uploaded is not None:
    df = pd.read_csv(uploaded)
    cols = {c.lower(): c for c in df.columns}
    lat = cols.get("lat"); lon = cols.get("lon")
    if not lat or not lon:
        st.error("Le CSV doit contenir les colonnes lat, lon.")
    else:
        st.map(df.rename(columns={lat:"lat", lon:"lon"}))
else:
    st.write("Chargez un CSV pour afficher la carte.")
