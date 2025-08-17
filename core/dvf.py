
import pandas as pd

def load_dvf_medians(dvf_df):
    """Expect columns: city, zipcode(optional), property_type(optional), median_price_sqm"""
    if dvf_df is None or dvf_df.empty:
        return None
    # normalize
    cols = {c.lower(): c for c in dvf_df.columns}
    required = cols.get("city"), cols.get("median_price_sqm")
    if any(c is None for c in required):
        raise ValueError("DVF medians CSV doit contenir au minimum: city, median_price_sqm")
    return dvf_df

def price_gap_vs_dvf(price, surface_m2, city, dvf_df):
    """Return % gap of listing price/m² vs DVF median for the city's property type if available."""
    if dvf_df is None or dvf_df.empty or surface_m2 <= 0:
        return None
    cols = {c.lower(): c for c in dvf_df.columns}
    city_col = cols.get("city"); med_col = cols.get("median_price_sqm"); pt_col = cols.get("property_type")
    sub = dvf_df[dvf_df[city_col].str.lower() == str(city).lower()]
    if sub.empty:
        return None
    # Try match on property_type if present
    if pt_col and pt_col in dvf_df.columns and "property_type" in cols:
        # not strict; if not found, use any for city
        pass
    med = float(sub.iloc[0][med_col])
    if med <= 0:
        return None
    listing_ppm2 = price / surface_m2
    return (listing_ppm2 - med) / med * 100.0
