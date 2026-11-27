from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data import clean

# Paths relative to the project root
DATA_PATH = Path("data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv")
MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "churn_model.joblib"


def build_pipeline(X: pd.DataFrame) -> Pipeline:
    """Build the leak-proof preprocessing + Logistic Regression pipeline."""
    num_cols = X.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = X.select_dtypes(exclude=["number"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                num_cols,
            ),
            (
                "cat",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                ]),
                cat_cols,
            ),
        ]
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(max_iter=1000, random_state=42)),
    ])


def main() -> None:
    # 1. Load & clean data using the shared function
    raw_df = pd.read_csv(DATA_PATH)
    df = clean(raw_df)

    # 2. Separate features and binary target
    X = df.drop(columns=["Churn"])
    y = (
        df["Churn"].map({"Yes": 1, "No": 0}).astype(int)
        if pd.api.types.is_string_dtype(df["Churn"])
        else df["Churn"].astype(int)
    )

    # 3. Fit pipeline on all 7,043 customers
    pipe = build_pipeline(X)
    pipe.fit(X, y)

    # 4. Save trained model artifact
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    print(f"Trained on {len(X)} records and saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
