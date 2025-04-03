-- primary key, error code, resolve (boolean), resolve date
CREATE TABLE error_reasons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    label TEXT NOT NULL,
    description TEXT
);
