# RECO Machine Learning Discrepancy Model

This README provides a complete overview of how the RECO machine learning pipeline works, including local training, model usage via API, and how the AI learns from human-labeled discrepancy resolutions.

---

## 🔍 Overview

RECO is an automated reconciliation platform designed to detect and classify financial discrepancies between internal (lender) and external (custodian bank) transaction records. This system:

- Extracts data from PostgreSQL tables populated by AWS Glue (or local uploads).
- Allows a human to resolve discrepancies and log them.
- Trains a local machine learning model based on those logged decisions.
- Uses the model to predict likely discrepancy reasons for unresolved mismatches.
- Provides predictions via a lightweight Flask API (`predictor.py`).

---

## 🌐 System Components

### 1. PostgreSQL (via Docker)
Manages structured data for transactions and reconciliations.

- `geneva_transactions` - Internal source (lender)
- `custodian_transactions` - External source (agent bank)
- `reconciliations` - Logs resolved discrepancies with labels
- `error_reasons` - Lookup table for discrepancy types

### 2. Python Scripts

- `train_model.py`: Extracts data, engineers features, trains a RandomForest model.
- `predictor.py`: Flask API that serves predictions using the trained model.

### 3. Model Artifact

- `reco_discrepancy_model.pkl`: Serialized model saved after training.

---

## 🔧 Setup Instructions

### Step 1: Spin up the local environment

Make sure Docker is running and run:

```bash
docker-compose up -d
```

This starts PostgreSQL, Adminer (UI at localhost:8080), and MinIO.

### Step 2: Install Python dependencies

```bash
pip install pandas scikit-learn psycopg2-binary fuzzywuzzy python-Levenshtein flask joblib
```

### Step 3: Prepare your PostgreSQL database

- Load tables using your SQL files:
  - `geneva-03-06.sql`
  - `custodian_bank-03-06.sql`
  - `error_reasons.sql`
- Create the `reconciliations` table:

```sql
CREATE TABLE reconciliations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    internal_transaction_id UUID REFERENCES geneva_transactions(id),
    external_transaction_id UUID REFERENCES custodian_transactions(id),
    error_reason_id INT REFERENCES error_reasons(id),
    resolution TEXT,
    label TEXT,
    resolved_by TEXT,
    resolved_at TIMESTAMP DEFAULT now()
);
```

### Step 4: Train the model

Once you have reconciled entries in the `reconciliations` table:

```bash
python train_model.py
```

- Trains a Random Forest model
- Computes `amount_diff`, `date_diff_days`, `currency_mismatch`, and `reference_similarity`
- Saves the model as `reco_discrepancy_model.pkl`

---

## 🔮 Example Training Output

```bash
🔍 Model Evaluation:
              precision    recall  f1-score   support

 FX_MISMATCH       0.88      0.85      0.86        40
     TIMING        0.91      0.93      0.92        30
DUPLICATE_ENTRY    0.89      0.87      0.88        20

accuracy                           0.89        90
```

---

## 💡 Using the Flask API

### Step 1: Run the API locally

```bash
python predictor.py
```

Runs on `http://localhost:5001`

### Step 2: Make a prediction request

#### Sample Request (via curl):
```bash
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "internal": {
      "amount": 100.00,
      "date": "2024-03-30",
      "currency": "USD",
      "reference_id": "TX123"
    },
    "external": {
      "amount": 101.00,
      "date": "2024-03-31",
      "currency": "EUR",
      "reference_id": "TX124"
    }
  }'
```

#### Sample Response:
```json
{
  "predicted_reason": "FX_MISMATCH",
  "confidence": 0.873
}
```

---

## 🤖 "Man in the Middle" Learning Loop

1. You resolve a discrepancy and enter it in `reconciliations`
2. You label the resolution (e.g., `FX_MISMATCH`)
3. That record is used to train the model (`train_model.py`)
4. The model learns patterns between Geneva and Custodian data
5. New discrepancies are passed to `predictor.py`
6. Model gives its best guess with confidence
7. You accept or override the prediction
8. Overridden predictions improve the next training cycle

---

## ✅ Future Enhancements

- Add confidence threshold handling (e.g., auto-resolve if >95%)
- Add retrain-on-schedule cron job
- Visual dashboard for prediction/actual comparisons
- Auto-log all predictions made with audit trail

---

## 🚀 Summary

The RECO discrepancy model gives your team a powerful AI assistant that:
- Learns from human decisions
- Predicts likely mismatch types
- Helps reduce manual reconciliation time
- Improves with each new labeled example

Run it locally. Train it often. Let it assist you, then teach it to do more.

Let the model work *with* your analysts — not replace them.

