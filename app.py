from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

from src.data import clean

MODEL_PATH = Path("models/churn_model.joblib")

st.set_page_config(page_title="Telco Churn Retention Scorer", layout="wide")
st.title("Telco Customer Churn Retention Scorer")
st.markdown(
    "Upload customer account data to calculate churn risk, determine the profit-optimal "
    "calling cutoff, and download a prioritized retention call list."
)


@st.cache_resource
def load_model(path: Path):
    return joblib.load(path)


if not MODEL_PATH.exists():
    st.error(
        f"Model file not found at `{MODEL_PATH}`. "
        "Please run `python -m src.train` from the project root first."
    )
    st.stop()

model = load_model(MODEL_PATH)

# --- Sidebar: Business Economics Inputs ---
st.sidebar.header("Campaign Economics")
call_cost = st.sidebar.number_input(
    "Call Cost ($)", min_value=1.0, max_value=1000.0, value=50.0, step=5.0
)
customer_value = st.sidebar.number_input(
    "Customer Value ($)", min_value=10.0, max_value=10000.0, value=500.0, step=25.0
)
success_rate_pct = st.sidebar.number_input(
    "Offer Success Rate (%)", min_value=1.0, max_value=100.0, value=30.0, step=1.0
)

success_rate = success_rate_pct / 100.0
expected_save_value = customer_value * success_rate
threshold = min(call_cost / expected_save_value, 1.0)

st.sidebar.markdown("---")
st.sidebar.metric("Breakeven Probability Threshold", f"{threshold:.1%}")
st.sidebar.caption(
    f"Formula: `${call_cost:,.0f} / (${customer_value:,.0f} × {success_rate_pct:.0f}%) = {threshold:.3f}`"
)

# --- Main Area: CSV Upload & Scoring ---
uploaded_file = st.file_uploader(
    "Upload Customer CSV (same columns as Telco dataset, without Churn)",
    type=["csv"],
)

if uploaded_file is not None:
    # 1. Safely parse the uploaded CSV file
    try:
        raw_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(
            f"Could not read the uploaded file as a valid CSV. Please check the file format and try again. (Details: {e})"
        )
        st.stop()

    if raw_df.empty:
        st.error("The uploaded CSV file is empty. Please upload a file containing at least one customer row.")
        st.stop()

    # 2. Validate required columns against model.feature_names_in_
    expected_cols = list(model.feature_names_in_)
    missing_cols = [col for col in expected_cols if col not in raw_df.columns]

    if missing_cols:
        missing_str = ", ".join(missing_cols)
        st.error(
            f"Your uploaded file is missing the following required column(s): **{missing_str}**. "
            "Please upload a CSV matching the Telco customer schema."
        )
        st.stop()

    # Preserve customerID for the output table if present before clean() drops it
    customer_ids = (
        raw_df["customerID"].copy()
        if "customerID" in raw_df.columns
        else pd.Series(range(1, len(raw_df) + 1), name="Customer_Row")
    )

    # 3. Clean features and run model prediction safely
    try:
        features_df = clean(raw_df).drop(columns=["Churn"], errors="ignore")
        # Ensure columns match the exact order expected by the model
        features_df = features_df[expected_cols]
        probs = model.predict_proba(features_df)[:, 1]
    except Exception as e:
        st.error(
            "Unable to score the uploaded file. Please ensure numeric columns (such as `tenure` and "
            f"`MonthlyCharges`) contain valid numbers without invalid text. (Details: {e})"
        )
        st.stop()

    # Build results DataFrame
    results_df = raw_df.drop(columns=["Churn"], errors="ignore").copy()
    if "customerID" not in results_df.columns:
        results_df.insert(0, "customerID", customer_ids)

    results_df.insert(1, "Churn_Probability", probs)
    results_df.insert(
        2,
        "Action",
        ["Call" if p >= threshold else "Don't call" for p in probs],
    )

    # Sort highest risk first
    results_df = results_df.sort_values(
        by="Churn_Probability", ascending=False
    ).reset_index(drop=True)

    # Calculate campaign metrics
    call_mask = results_df["Action"] == "Call"
    n_to_call = int(call_mask.sum())
    expected_saves = results_df.loc[call_mask, "Churn_Probability"].sum()
    expected_profit = (expected_saves * expected_save_value) - (n_to_call * call_cost)

    # --- Top Summary KPIs ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers Scored", f"{len(results_df):,}")
    col2.metric("Customers to Call", f"{n_to_call:,} ({n_to_call / len(results_df):.1%})")
    col3.metric("Breakeven Cutoff", f"{threshold:.1%}")
    col4.metric("Expected Net Profit", f"${expected_profit:,.2f}")

    # --- Risk-Sorted Table ---
    st.subheader("Customer Risk Ranking")
    display_df = results_df.copy()
    display_df["Churn_Probability"] = display_df["Churn_Probability"].map(
        lambda x: f"{x:.1%}"
    )
    st.dataframe(display_df, use_container_width=True)

    # --- Download Call List Only ---
    call_list_df = results_df[call_mask].copy()
    csv_bytes = call_list_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=f"Download Call List CSV ({n_to_call} customers)",
        data=csv_bytes,
        file_name="retention_call_list.csv",
        mime="text/csv",
    )
else:
    st.info(
        "Upload a CSV file above (for example, `data/sample_customers.csv`) to generate risk scores and a call list."
    )
