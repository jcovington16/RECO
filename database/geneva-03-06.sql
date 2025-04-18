-- Creation of Geneva table 03-06-2025
DROP TABLE IF EXISTS geneva; 

CREATE TABLE IF NOT EXISTS geneva (
    id SERIAL PRIMARY KEY,
    interface_type VARCHAR(255) NOT NULL,
    from_close_date DATE NOT NULL,
    to_close_date DATE NOT NULL,
    fund_id VARCHAR(255) NOT NULL,
    issuer_id BIGINT NOT NULL,
    issuer_name VARCHAR(255) NOT NULL,
    issuer_contra_fund_id VARCHAR(255),
    asset_name VARCHAR(50) NOT NULL,
    asset_abbrev VARCHAR(50) NOT NULL,
    asset_id BIGINT NOT NULL,
    cusip VARCHAR(9),
    isin VARCHAR(12) NOT NULL,
    loanx VARCHAR(15) NOT NULL,
    asset_type VARCHAR(25) NOT NULL,
    asset_class VARCHAR(25) NOT NULL,
    asset_class_name VARCHAR(25) NOT NULL,
    clearing_account_id VARCHAR(15) NOT NULL,
    clearing_account_name VARCHAR(25) NOT NULL,
    currency_id VARCHAR(15) NOT NULL,
    td_amount INT NOT NULL,
    sd_amount INT NOT NULL,
    effective_date DATE NOT NULL,
    settle_date DATE NOT NULL,
    event_xsrc VARCHAR(25),
    event_id_xref VARCHAR(25),
    trade_id INT NOT NULL,
    geneva_comments VARCHAR(255),
    geneva_portfolio_event_type VARCHAR(25) NOT NULL,
    common_asset_id INT NOT NULL,
    recon_date DATE NOT NULL,
    recon_amount INT NOT NULL,
    recon_account_id VARCHAR(25) NOT NULL,
    recon_account_name VARCHAR(25) NOT NULL,
    min_journal_amount_id INT NOT NULL,
    max_journal_amount_id INT NOT NULL,
    ad_amount INT NOT NULL,
    axiom_product_id INT NOT NULL
    -- FOREIGN KEY (bank_id) REFERENCES bank(id) ON DELETE CASCADE
)
