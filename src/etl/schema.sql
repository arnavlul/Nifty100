PRAGMA foreign_keys = ON;

CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    name TEXT,
    ticker TEXT,
    sector_id INTEGER
);

CREATE TABLE profitandloss (
    company_id INTEGER,
    year INTEGER,
    sales REAL,
    net_profit REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE balancesheet (
    company_id INTEGER,
    year INTEGER,
    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    total_assets REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE cashflow (
    company_id INTEGER,
    year INTEGER,
    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE analysis (
    analysis_id INTEGER PRIMARY KEY
);

CREATE TABLE documents (
    document_id INTEGER PRIMARY KEY
);

CREATE TABLE prosandcons (
    pc_id INTEGER PRIMARY KEY
);

CREATE TABLE sectors (
    sector_id INTEGER PRIMARY KEY,
    broad_sector TEXT
);

CREATE TABLE stock_prices (
    company_id INTEGER,
    year INTEGER,
    price REAL,
    PRIMARY KEY (company_id, year)
);

CREATE TABLE financial_ratios (
    company_id INTEGER,
    year INTEGER,
    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    debt_to_equity REAL,
    interest_coverage REAL,
    asset_turnover REAL,
    free_cash_flow_cr REAL,
    capex_cr REAL,
    earnings_per_share REAL,
    book_value_per_share REAL,
    dividend_payout_ratio_pct REAL,
    total_debt_cr REAL,
    cash_from_operations_cr REAL,
    revenue_cagr_5yr REAL,
    pat_cagr_5yr REAL,
    eps_cagr_5yr REAL,
    composite_quality_score REAL,
    PRIMARY KEY (company_id, year)
);

CREATE TABLE peer_groups (
    group_id INTEGER PRIMARY KEY
);
