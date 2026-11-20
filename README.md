# Telco Customer Churn Analysis

## Business Problem
Customer churn directly impacts recurring revenue and increases customer acquisition costs for telecommunications providers. The objective of this project is to identify the primary demographic, account, billing, and service factors driving customer cancellations and build a baseline predictive model so the business can deploy targeted retention strategies and reduce overall churn.

## Data
- **Source:** Telco Customer Churn dataset (`7,043` customer records across `21` features).
- **Target Variable:** `Churn` (binary indicator showing whether a customer left within the last month: `Yes` or `No`).
- **Key Features Analyzed:**
  - **Account & Contract:** `tenure` (months with the company), `Contract`, `PaperlessBilling`, `PaymentMethod`, `MonthlyCharges`, and `TotalCharges`.
  - **Services:** `InternetService` (`DSL`, `Fiber optic`, `No`) and add-on subscriptions.
  - **Demographics:** `gender`, `SeniorCitizen`, `Partner`, and `Dependents`.
- **Data Cleaning & Imputation:**
  - Converted `TotalCharges` from string format to `float64`.
  - Missing values in `TotalCharges` (found exclusively among brand-new customers with `tenure == 0`) were imputed using `MonthlyCharges × tenure` (resulting in `$0.00` for customers who have not yet completed their first billing cycle).

## Key Findings

**Overall Churn Rate:** **26.5%** (`1,869` churned out of `7,043` total customers).

### 1. Month-to-Month Contracts Drive the Vast Majority of Cancellations
- **Flexible contracts carry extreme churn risk.** Customers on **Month-to-month** agreements churn at **42.7%** (`n = 3,875`), which is nearly **4x higher** than One-year contracts at **11.3%** (`n = 1,473`) and **15x higher** than Two-year contracts at **2.8%** (`n = 1,695`).
- **Hypothesis:** Without annual commitment or early-termination friction, month-to-month subscribers treat the service as easily replaceable whenever they encounter price increases, billing friction, or competitor promotions.

### 2. The First Year Is the Critical Danger Zone (Tenure)
- **Nearly half of new customers leave within their first year.** Customers in the **0–12 month** bracket churn at **47.4%** (`n = 2,186`), making onboarding and early engagement the highest-leverage retention opportunity.
- **Retention strengthens dramatically over time.** Once a customer passes the 1-year mark, churn drops sharply to **28.7%** (`13–24m`, `n = 1,024`), **21.6%** (`25–36m`, `n = 832`), **19.0%** (`37–48m`, `n = 762`), **14.4%** (`49–60m`, `n = 832`), and down to **6.6%** for customers staying beyond 5 years (`61–72m`, `n = 1,407`).
- **Hypothesis:** Early churn reflects unmet expectations during onboarding and initial billing cycles, whereas customers who survive the first year have integrated the service into their household routine and are likely locked into multi-year contracts.

### 3. Electronic Check Churn Is Driven by Both Contract Overlap and Payment Friction
- **Electronic check users churn nearly 3x more than auto-pay customers.** Overall, **Electronic check** users churn at **45.3%** (`n = 2,365`), compared to **19.1%** for Mailed check (`n = 1,612`), **16.7%** for Bank transfer (`n = 1,544`), and **15.2%** for Credit card (`n = 1,522`).
- **Cross-tabulation reveals heavy overlap with Month-to-month contracts—but a persistent gap within every tier:**
  - **78.2%** of all Electronic check users (`1,850` of `2,365`) are on **Month-to-month** plans, where their churn reaches **53.7%** (`n = 1,850`)—far above Month-to-month customers using Bank transfer (**34.1%**, `n = 589`), Credit card (**32.8%**, `n = 543`), or Mailed check (**31.6%**, `n = 893`).
  - Even on **One-year** (`18.4%`, `n = 347` vs. `6.8%–10.3%` for other methods) and **Two-year** contracts (`7.7%`, `n = 168` vs. `0.8%–3.4%`), Electronic check users still churn at roughly double the rate of other payment methods.
- **Hypothesis:** High churn among Electronic check users is a two-part effect: (1) heavy concentration in flexible Month-to-month contracts, and (2) active monthly billing friction—unlike automatic payments that run silently in the background, manual electronic checks force customers to actively review and approve their bill every month, creating a recurring decision point to cancel.

### 4. Fiber Optic Customers Churn at More Than Double the Rate of DSL
- **Fiber optic internet is the highest-risk product segment.** Fiber optic subscribers churn at **41.9%** (`n = 3,096`), compared to **19.0%** for DSL (`n = 2,421`) and **7.4%** for customers without internet service (`n = 1,526`).
- **Hypothesis:** Elevated churn among Fiber optic users likely stems from higher monthly price sensitivity (`MonthlyCharges`), higher expectations for speed/reliability, or heavy overlap with Month-to-month and Electronic check cohorts rather than dissatisfaction with fiber technology itself.

### 5. Paperless Billing and Single-Member Households Show Higher Churn
- **Paperless billing shows elevated churn.** Customers using paperless billing churn at **33.6%** (`n = 4,171`), more than double the **16.3%** churn rate of traditional paper billing (`n = 2,872`).
- **Single-member households leave more frequently.** Customers without a partner churn at **33.0%** (`n = 3,641`) vs. **19.7%** with a partner (`n = 3,402`), and customers without dependents churn at **31.3%** (`n = 4,933`) vs. **15.5%** with dependents (`n = 2,110`).
- **Hypothesis:** Paperless billing likely acts as a proxy for digital-first Month-to-month/Electronic check segments, while single-member households face lower switching costs because fewer people rely on the home connection.

## Deep-Dive: Why Do Electronic-Check Users Churn More & How to Test It?

### Why Electronic-Check Users Churn More
1. **Contract Self-Selection (Proven in Cross-Tab Check):** Nearly 4 out of 5 Electronic check users (`1,850` of `2,365`) choose Month-to-month contracts, meaning they self-select into maximum flexibility and low commitment from day one.
2. **Active Billing Friction ("The Monthly Reminder Effect"):** Automatic credit card and bank transfers happen passively, whereas paying by electronic check requires manual action each month. Every manual payment forces the customer to notice the exact dollar amount leaving their account—triggering price sensitivity and cancellation decisions.
3. **Price & Service Tier Overlap (To Be Tested):** Electronic check users may disproportionately subscribe to expensive **Fiber optic** plans (`MonthlyCharges`) without retention-anchoring add-ons like `TechSupport` or `OnlineSecurity`, amplifying sticker shock every billing cycle.

### How to Test the Remaining Hypotheses
- **Check 1 — Price & Service Tier Overlap (`InternetService` × `PaymentMethod` × `MonthlyCharges`):** Cross-tabulate `PaymentMethod` against `InternetService` and compare median `MonthlyCharges` across payment methods to test whether Electronic check users pay higher monthly bills than auto-pay customers.
- **Check 2 — Add-On Retention Anchors (`TechSupport` & `OnlineSecurity`):** Within the `Month-to-month + Electronic check` cohort (`n = 1,850`), compare churn rates between customers with `TechSupport == "Yes"` vs. `"No"` and `OnlineSecurity == "Yes"` vs. `"No"`.
- **Check 3 — Tenure Distribution by Payment Method:** Compare median `tenure` across the four `PaymentMethod` groups to verify whether Electronic check users skew heavily toward brand-new customers (`0–12m`).

## Baseline Modeling & Evaluation

### Methodology
- **Train/Test Split:** Stratified 80/20 split (`5,634` train / `1,409` test records, `random_state=42`) to preserve the exact **26.5%** churn distribution across both sets.
- **Leak-Proof Preprocessing (`ColumnTransformer`):**
  - Numeric features (`tenure`, `MonthlyCharges`, `TotalCharges`, `SeniorCitizen`) imputed with median and standardized via `StandardScaler`.
  - Categorical features imputed with most frequent category and encoded via `OneHotEncoder(handle_unknown="ignore")`.
  - All transformations fitted strictly on `X_train` inside Scikit-Learn `Pipeline` objects to prevent data leakage.
- **Evaluation Metrics:**
  - **ROC AUC:** Measures overall ranking discrimination across all classification thresholds.
  - **Precision @ Top 20%:** Ranks test customers by predicted churn probability and measures the actual churn rate among the top 20% highest-risk customers (`n = 281`), reflecting real-world retention campaign capacity.

### Results

| Model | ROC AUC | Precision @ Top 20% | Lift over Baseline |
| :--- | :---: | :---: | :---: |
| **Dummy Classifier** (`most_frequent`) | `0.5000` | `28.1%` (`0.2811`) | 1.00x (Baseline) |
| **Logistic Regression** | `0.8421` | `66.2%` (`0.6619`) | **2.35x** |

- **Takeaway:** Ranking customers with Logistic Regression more than doubles retention targeting efficiency compared to untargeted outreach (`2.35x` lift), capturing **66.2%** actual churners (`186` of `281` flagged customers) within the top 20% highest-risk segment.

## Recommended Action Items
- **Score & Target the Top 20% Highest-Risk Customers:** Deploy the Logistic Regression risk score monthly to prioritize retention outreach toward the top 20% highest-probability churners (`66.2%` precision) rather than running untargeted campaigns.
- **Bundle Auto-Pay + Contract Upgrades for Electronic Check Users:** Target the **1,850 Month-to-month Electronic check customers** (`53.7%` churn) with a combined incentive—such as a `$5/month` bill credit or waived fee—when they enroll in automatic payments alongside a 1-year contract.
- **Launch a First-Year Onboarding Program:** Target new customers in months **0–12** (`47.4%` churn) with proactive check-ins and loyalty milestones to guide them past the critical first-year drop-off window.
