import pandas as pd
import psycopg2
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from fuzzywuzzy import fuzz
import joblib
import warnings
warnings.filterwarnings("ignore")

# --- Database connection ---
conn = psycopg2.connect(
    dbname="reco_db",
    user="reco_user",
    password="reco_pass",
    host="localhost",
    port="5433"
)

# --- Query reconciled data ---
query = """
SELECT 
    r.id AS rec_id,
    g.amount AS internal_amount,
    g.transaction_date AS internal_date,
    g.currency AS internal_currency,
    g.reference_id AS internal_ref,

    c.amount AS external_amount,
    c.transaction_date AS external_date,
    c.currency AS external_currency,
    c.reference_id AS external_ref,

    e.code AS error_code
FROM reconciliations r
JOIN geneva_transactions g ON r.internal_transaction_id = g.id
JOIN custodian_transactions c ON r.external_transaction_id = c.id
JOIN error_reasons e ON r.error_reason_id = e.id
WHERE r.label IS NOT NULL
"""

df = pd.read_sql(query, conn)

# --- Feature Engineering ---
def compute_features(row):
    return pd.Series({
        'amount_diff': abs(row['internal_amount'] - row['external_amount']),
        'date_diff_days': abs((row['internal_date'] - row['external_date']).days),
        'currency_mismatch': int(row['internal_currency'] != row['external_currency']),
        'reference_similarity': fuzz.ratio(str(row['internal_ref']), str(row['external_ref']))
    })

features_df = df.apply(compute_features, axis=1)
features_df['label'] = df['error_code']

# --- Train/Test Split ---
X = features_df.drop(columns=['label'])
y = features_df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# --- Train Model ---
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# --- Save Model ---
joblib.dump(clf, 'reco_discrepancy_model.pkl')

# --- Evaluation ---
y_pred = clf.predict(X_test)
print("🔍 Model Evaluation:\n")
print(classification_report(y_test, y_pred))
print("✅ Model trained and saved as 'reco_discrepancy_model.pkl'")

# --- Optional: Predict for unresolved mismatches (man-in-the-middle mode) ---
print("\n--- Top predictions for unresolved mismatches ---")

unresolved_query = """
SELECT 
    g.amount AS internal_amount,
    g.transaction_date AS internal_date,
    g.currency AS internal_currency,
    g.reference_id AS internal_ref,

    c.amount AS external_amount,
    c.transaction_date AS external_date,
    c.currency AS external_currency,
    c.reference_id AS external_ref
FROM geneva_transactions g
JOIN custodian_transactions c ON g.reference_id = c.reference_id
WHERE NOT EXISTS (
    SELECT 1 FROM reconciliations r
    WHERE r.internal_transaction_id = g.id AND r.external_transaction_id = c.id
)
LIMIT 10;
"""

unresolved_df = pd.read_sql(unresolved_query, conn)

if not unresolved_df.empty:
    pred_features = unresolved_df.apply(compute_features, axis=1)
    pred_probs = clf.predict_proba(pred_features)
    pred_labels = clf.classes_[pred_probs.argmax(axis=1)]

    unresolved_df['predicted_reason'] = pred_labels
    unresolved_df['confidence'] = pred_probs.max(axis=1)

    print(unresolved_df[['internal_ref', 'external_ref', 'predicted_reason', 'confidence']])
else:
    print("No unresolved items found.")

conn.close()
