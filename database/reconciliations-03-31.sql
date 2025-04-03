CREATE TABLE reconciliations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    internal_transaction_id UUID REFERENCES geneva_transactions(id),
    external_transaction_id UUID REFERENCES custodian_transactions(id),

    error_reason_id INT REFERENCES error_reasons(id),  -- Optional but useful
    resolution TEXT, -- Free text from analyst
    label TEXT,      -- Classification label for ML model

    resolved_by TEXT,
    resolved_at TIMESTAMP DEFAULT now()
);
