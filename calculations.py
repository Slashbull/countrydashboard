# calculations.py
import pandas as pd

def calculate_kpis(df: pd.DataFrame) -> dict:
    total_tons = df["Tons"].sum() if "Tons" in df.columns else 0
    if "Date" in df.columns:
        monthly = df.groupby(pd.Grouper(key="Date", freq="M"))["Tons"].sum()
        avg_monthly = monthly.mean()
    else:
        avg_monthly = 0
    return {"total_tons": total_tons, "avg_monthly": avg_monthly}
