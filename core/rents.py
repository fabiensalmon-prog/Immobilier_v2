
import pandas as pd

def normalize_cols(df):
    return {c.lower(): c for c in df.columns}

def estimate_rent_per_m2(city, property_type, bench_df, fallback_per_city):
    city_key = city.lower().strip()
    pt_key = (property_type or "all").lower().strip()
    if bench_df is None or bench_df.empty:
        return fallback_per_city.get(city_key, fallback_per_city.get("default", 20.0))
    cols = normalize_cols(bench_df)
    city_col = cols.get("city"); pt_col = cols.get("property_type"); rpm2_col = cols.get("rent_per_m2")
    if not city_col or not rpm2_col:
        return fallback_per_city.get(city_key, fallback_per_city.get("default", 20.0))
    df_city = bench_df[bench_df[city_col].str.lower() == city_key]
    if pt_col and pt_key:
        df_ct = df_city[df_city[pt_col].str.lower() == pt_key]
        if not df_ct.empty:
            return float(df_ct.iloc[0][rpm2_col])
    if not df_city.empty:
        return float(df_city.iloc[0][rpm2_col])
    return fallback_per_city.get(city_key, fallback_per_city.get("default", 20.0))

def apply_rent_cap(total_rent, surface_m2, cap_per_m2=None, apply_cap=False):
    if not apply_cap or not cap_per_m2 or cap_per_m2 <= 0:
        return total_rent
    return min(total_rent, cap_per_m2 * surface_m2)
