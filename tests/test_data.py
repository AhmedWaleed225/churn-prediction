import pandas as pd
from src.data import clean


def _sample_raw_df() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "customerID": "7590-VHVEG",
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "No",
            "tenure": 1,
            "PhoneService": "No",
            "MultipleLines": "No phone service",
            "InternetService": "DSL",
            "OnlineSecurity": "No",
            "OnlineBackup": "Yes",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 29.85,
            "TotalCharges": "29.85",
            "Churn": "No",
        },
        {
            "customerID": "0000-NEWCUST",
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 0,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "One year",
            "PaperlessBilling": "No",
            "PaymentMethod": "Mailed check",
            "MonthlyCharges": 56.95,
            "TotalCharges": " ",  # Blank string typical of tenure == 0
            "Churn": "No",
        },
    ])


def test_total_charges_converted_and_no_missing_values():
    raw_df = _sample_raw_df()
    cleaned_df = clean(raw_df)

    assert cleaned_df["TotalCharges"].isna().sum() == 0
    assert pd.api.types.is_float_dtype(cleaned_df["TotalCharges"])
    assert cleaned_df.loc[1, "TotalCharges"] == 0.0


def test_customer_id_is_dropped():
    raw_df = _sample_raw_df()
    cleaned_df = clean(raw_df)

    assert "customerID" not in cleaned_df.columns
