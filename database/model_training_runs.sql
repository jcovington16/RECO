CREATE TABLE model_training_runs (
    id SERIAL PRIMARY KEY,
    trained_at TIMESTAMP DEFAULT now(),
    accuracy FLOAT,
    total_examples INT
);
