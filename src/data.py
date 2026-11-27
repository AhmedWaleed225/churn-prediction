import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw Telco Customer Churn data for training or inference.
    - Converts TotalCharges from string to float64.
    - Fills missing TotalCharges (tenure == 0) with MonthlyCharges * tenure.
    - Drops customerID and any temporary EDA columns if present.
    """
    df = df.copy()

    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        if "MonthlyCharges" in df.columns and "tenure" in df.columns:
            df["TotalCharges"] = df["TotalCharges"].fillna(
                df["MonthlyCharges"] * df["tenure"]
            )

    df = df.drop(columns=["customerID", "tenure_group"], errors="ignore")
    return df
