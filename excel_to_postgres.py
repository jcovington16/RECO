# #!/usr/bin/env python3
# """
# CSV to PostgreSQL Importer
# -------------------------
# This script imports data from CSV files into PostgreSQL tables,
# specifically optimized for the Geneva table structure.
# """

# import pandas as pd
# import psycopg2
# import numpy as np
# import re
# import sys
# from datetime import datetime

# # Database Connection Parameters
# DB_CONFIG = {
#     'host': 'localhost',
#     'port': 5433,
#     'database': 'reco_db',
#     'user': 'reco_user',
#     'password': 'reco_pass'
# }

# # CSV File Configuration
# CUSTODIAN_CSV = 'BAnk Cash'
# GENEVA_CSV = 'GVA Cash ledger.csv'

# # Explicit mapping for Geneva columns
# CUSTODIAN_MAPPING = {
#     'Account Number': 'account_number',
#     'Account Name': 'account_name',
#     'Cash Account Number': 'cash_account_number',
#     'Cash Account Name': 'cash_account_name',
#     'Reporting Currency Name': 'reporting_currency_name',
#     'Local Currency Code': 'local_currency_code',
#     'Local Currency Name': 'local_currency_name',
#     'Location Code': 'location_code',
#     'Location Name': 'location_name',
#     'Cash Reporting Date': 'cash_reporting_date',
#     'Settle / Pay Date': 'settle_pay_date',
#     'Tax Code': 'tax_code',
#     'Transaction Type Code': 'transaction_type_code',
#     'Transaction Type': 'transaction_type',
#     'Main Transaction Code': 'main_transaction_code',
#     'Sub Transaction Code': 'sub_transaction_code',
#     'Detailed Transaction Type Name': 'detailed_transaction_type_name',
#     'Transaction Description 1': 'transaction_description_1',
#     'Transaction Description 3': 'transaction_description_3',
#     'Transaction Description 4': 'transaction_description_4',
#     'Transaction Description 5': 'transaction_description_5',
#     'Actual Settle Date': 'actual_settle_date',
#     'Alternate Delivery Date': 'alternate_delivery_date',
#     'Record Date': 'record_date',
#     'Cash Post Date': 'cash_post_date',
#     'Cash Value Date': 'cash_value_date',
#     'Shares / Par': 'shares_par',
#     'Opening Balance Local': 'opening_balance_local',
#     'Transaction Amount Local': 'transaction_amount_local',
#     'Closing Balance Local': 'closing_balance_local',
#     'Transaction Amount Reporting Equivalent': 'transaction_amount_reporting_equivalent',
#     'Begin Date': 'begin_date',
#     'End Date': 'end_date',
#     'Report Run Date': 'report_run_date',
#     'Report Run Time': 'report_run_time',
#     'Current Factor': 'current_factor',
#     'Previous Factor': 'previous_factor',
#     'Event ID': 'event_id',
#     'Flat Tax %': 'flat_tax_percent',
#     'Flat Tax Amount': 'flat_tax_amount',
#     'Solidarity %': 'solidarity_percent',
#     'Solidarity Amount': 'solidarity_amount',
#     'Flat Tax Currency': 'flat_tax_currency'
# }

# GENEVA_COLUMN_MAP = {
#     'InterfaceType': 'interface_type',
#     'FromCloseDate': 'from_close_date',
#     'ToCloseDate': 'to_close_date',
#     'FundID': 'fund_id',
#     'IssuerID': 'issuer_id',
#     'IssuerName': 'issuer_name',
#     'IssuerContraFundID': 'issuer_contra_fund_id',
#     'AssetName': 'asset_name',
#     'AssetAbbrev': 'asset_abbrev',
#     'AssetID': 'asset_id',
#     'CUSIP': 'cusip',
#     'ISIN': 'isin',
#     'LoanX': 'loanx',
#     'AssetType': 'asset_type',
#     'AssetClass': 'asset_class',
#     'AssetClassName': 'asset_class_name',
#     'ClearingAccountID': 'clearing_account_id',
#     'ClearingAccountName': 'clearing_account_name',
#     'CurrencyID': 'currency_id',
#     'TDAmount': 'td_amount',
#     'SDAmount': 'sd_amount',
#     'EffectiveDate': 'effective_date',
#     'SettleDate': 'settle_date',
#     'EventXsrc': 'event_xsrc',
#     'EventIDXref': 'event_id_xref',
#     'TradeID': 'trade_id',
#     'GenevaComments': 'geneva_comments',
#     'GenevaPortfolioEventType': 'geneva_portfolio_event_type',
#     'CommonAssetID': 'common_asset_id',
#     'ReconDate': 'recon_date',
#     'ReconAmount': 'recon_amount',
#     'ReconAccountID': 'recon_account_id',
#     'ReconAccountName': 'recon_account_name',
#     'MinJournalAmountID': 'min_journal_amount_id',
#     'MaxJournalAmountID': 'max_journal_amount_id',
#     'ADAmount': 'ad_amount',
#     'AxiomProductID': 'axiom_product_id'
# }

# def connect_to_db():
#     """Create a connection to the database."""
#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         return conn
#     except psycopg2.Error as e:
#         print(f"❌ Database connection error: {e}")
#         sys.exit(1)

# def modify_schema(conn):
#     """Modify database schema to handle all data types."""
#     cursor = conn.cursor()
    
#     try:
#         # Update ALL columns in geneva table to TEXT
#         cursor.execute("""
#             SELECT column_name, data_type, is_nullable 
#             FROM information_schema.columns 
#             WHERE table_name = 'geneva' AND column_name != 'id'
#         """)
        
#         geneva_columns = cursor.fetchall()
#         for col, datatype, nullable in geneva_columns:
#             # Skip already TEXT columns
#             if datatype.lower() != 'text':
#                 print(f"  Converting geneva.{col} to TEXT type")
#                 cursor.execute(f"ALTER TABLE geneva ALTER COLUMN {col} TYPE TEXT USING {col}::TEXT")
            
#             # Make nullable
#             if nullable == 'NO':
#                 print(f"  Making geneva.{col} nullable")
#                 cursor.execute(f"ALTER TABLE geneva ALTER COLUMN {col} DROP NOT NULL")
        
#         conn.commit()
#         print("✅ Schema modified successfully")
    
#     except Exception as e:
#         conn.rollback()
#         print(f"❌ Error modifying schema: {e}")
#         raise
#     finally:
#         cursor.close()

# def clean_geneva_data(df):
#     """Process Geneva data for import."""
#     # Step 1: Drop unnamed columns
#     df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
#     # Step 2: Apply column mapping
#     df_renamed = pd.DataFrame()
#     found_columns = {}
    
#     # Track which columns we find and which we don't
#     for csv_col, db_col in GENEVA_COLUMN_MAP.items():
#         if csv_col in df.columns:
#             df_renamed[db_col] = df[csv_col]
#             found_columns[csv_col] = True
#         else:
#             found_columns[csv_col] = False
    
#     # Report on column mapping
#     print("\nColumn mapping results:")
#     for csv_col, found in found_columns.items():
#         status = "✅ Found" if found else "❌ Missing"
#         print(f"  {status}: {csv_col} → {GENEVA_COLUMN_MAP[csv_col]}")
    
#     # Step 3: Clean data values
#     for col in df_renamed.columns:
#         # Convert to string and clean
#         df_renamed[col] = df_renamed[col].astype(str)
        
#         # Clean commas from numeric strings
#         if col in ['td_amount', 'sd_amount', 'recon_amount', 'ad_amount']:
#             df_renamed[col] = df_renamed[col].apply(
#                 lambda x: x.replace(',', '') if isinstance(x, str) and ',' in x else x
#             )
        
#         # Replace NaN, None, 'nan', 'NaT' with empty string
#         df_renamed[col] = df_renamed[col].replace(['nan', 'NaN', 'NaT', 'None'], '')
    
#     return df_renamed

# def get_db_columns(conn, table_name):
#     """Get column names from a database table."""
#     cursor = conn.cursor()
#     try:
#         cursor.execute(f"""
#             SELECT column_name 
#             FROM information_schema.columns 
#             WHERE table_name = '{table_name}' 
#             AND column_name != 'id'
#         """)
#         columns = [row[0] for row in cursor.fetchall()]
#         return columns
#     finally:
#         cursor.close()

# def insert_geneva_data(conn, df):
#     """Insert Geneva data into database."""
#     cursor = conn.cursor()
#     rows_inserted = 0
    
#     try:
#         # Get database columns
#         db_columns = get_db_columns(conn, 'geneva')
#         print(f"Database columns: {len(db_columns)}")
#         print(f"DataFrame columns: {len(df.columns)}")
        
#         # Check columns match
#         missing_cols = [col for col in db_columns if col not in df.columns]
#         extra_cols = [col for col in df.columns if col not in db_columns]
        
#         if missing_cols:
#             print(f"Missing columns in dataframe: {missing_cols}")
#         if extra_cols:
#             print(f"Extra columns in dataframe: {extra_cols}")
            
#         # Filter to only include valid columns
#         df_filtered = df[[col for col in df.columns if col in db_columns]]
        
#         # Insert each row
#         for i, row in df_filtered.iterrows():
#             # Skip completely empty rows
#             if row.isnull().all():
#                 continue
                
#             # Build column lists and values
#             values = []
#             columns = []
            
#             for col, val in row.items():
#                 # Skip empty or NaN values
#                 if pd.isna(val) or val == '':
#                     continue
                    
#                 columns.append(col)
#                 # Escape single quotes in string values
#                 if isinstance(val, str):
#                     val = val.replace("'", "''")
#                 values.append(f"'{val}'")
            
#             # Skip if no valid columns
#             if not columns:
#                 continue
                
#             # Build SQL statement
#             column_str = ', '.join([f'"{col}"' for col in columns])
#             value_str = ', '.join(values)
            
#             sql = f'INSERT INTO geneva ({column_str}) VALUES ({value_str})'
            
#             try:
#                 cursor.execute(sql)
#                 rows_inserted += 1
                
#                 if rows_inserted % 5 == 0:
#                     conn.commit()
#                     print(f"✓ {rows_inserted} rows inserted")
                    
#             except Exception as e:
#                 conn.rollback()
#                 print(f"❌ Error on row {i}: {e}")
#                 print(f"SQL: {sql[:200]}...")
        
#         # Final commit
#         conn.commit()
#         return rows_inserted
    
#     finally:
#         cursor.close()

# def main():
#     print(f"📊 Starting Geneva Data Import")
    
#     try:
#         # Connect to the database
#         conn = connect_to_db()
#         print("✅ Connected to database")
        
#         # Modify schema
#         modify_schema(conn)
        
#         # Read CSV file
#         print(f"📖 Reading Geneva CSV file...")
#         geneva_df = pd.read_csv(GENEVA_CSV)
#         print(f"📝 Geneva CSV: {geneva_df.shape[0]} rows, {geneva_df.shape[1]} columns")
        
#         # Process data for import
#         print("🧹 Processing Geneva data...")
#         geneva_processed = clean_geneva_data(geneva_df)
        
#         # Clear existing data
#         print("🗑️ Clearing existing data...")
#         cursor = conn.cursor()
#         cursor.execute("TRUNCATE TABLE geneva RESTART IDENTITY")
#         conn.commit()
#         cursor.close()
        
#         # Insert data
#         print("📥 Inserting data into geneva table...")
#         inserted_count = insert_geneva_data(conn, geneva_processed)
        
#         # Report results
#         print("\n📊 Import Results:")
#         print(f"✅ Geneva table: {inserted_count} rows inserted")
#         print("✨ Import completed successfully!")
    
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         import traceback
#         traceback.print_exc()
    
#     finally:
#         if 'conn' in locals():
#             conn.close()
#             print("🔌 Database connection closed")

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
"""
CSV to PostgreSQL Importer
-------------------------
This script imports data from CSV files into PostgreSQL tables,
handling both Geneva and Custodian Bank data structures.
"""

import pandas as pd
import psycopg2
import numpy as np
import re
import sys
from datetime import datetime

# Database Connection Parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'reco_db',
    'user': 'reco_user',
    'password': 'reco_pass'
}

# CSV File Configuration
GENEVA_CSV = 'GVA Cash ledger.csv'
CUSTODIAN_CSV = 'BAnk Cash.csv'

# Explicit mapping for Geneva columns
GENEVA_COLUMN_MAP = {
    'InterfaceType': 'interface_type',
    'FromCloseDate': 'from_close_date',
    'ToCloseDate': 'to_close_date',
    'FundID': 'fund_id',
    'IssuerID': 'issuer_id',
    'IssuerName': 'issuer_name',
    'IssuerContraFundID': 'issuer_contra_fund_id',
    'AssetName': 'asset_name',
    'AssetAbbrev': 'asset_abbrev',
    'AssetID': 'asset_id',
    'CUSIP': 'cusip',
    'ISIN': 'isin',
    'LoanX': 'loanx',
    'AssetType': 'asset_type',
    'AssetClass': 'asset_class',
    'AssetClassName': 'asset_class_name',
    'ClearingAccountID': 'clearing_account_id',
    'ClearingAccountName': 'clearing_account_name',
    'CurrencyID': 'currency_id',
    'TDAmount': 'td_amount',
    'SDAmount': 'sd_amount',
    'EffectiveDate': 'effective_date',
    'SettleDate': 'settle_date',
    'EventXsrc': 'event_xsrc',
    'EventIDXref': 'event_id_xref',
    'TradeID': 'trade_id',
    'GenevaComments': 'geneva_comments',
    'GenevaPortfolioEventType': 'geneva_portfolio_event_type',
    'CommonAssetID': 'common_asset_id',
    'ReconDate': 'recon_date',
    'ReconAmount': 'recon_amount',
    'ReconAccountID': 'recon_account_id',
    'ReconAccountName': 'recon_account_name',
    'MinJournalAmountID': 'min_journal_amount_id',
    'MaxJournalAmountID': 'max_journal_amount_id',
    'ADAmount': 'ad_amount',
    'AxiomProductID': 'axiom_product_id'
}

# Explicit mapping for Custodian Bank columns
CUSTODIAN_COLUMN_MAP = {
    'Account Number': 'account_number',
    'Account Name': 'account_name',
    'Cash Account Number': 'cash_account_number',
    'Cash Account Name': 'cash_account_name',
    'Reporting Currency Name': 'reporting_currency_name',
    'Local Currency Code': 'local_currency_code',
    'Local Currency Name': 'local_currency_name',
    'Location Code': 'location_code',
    'Location Name': 'location_name',
    'Cash Reporting Date': 'cash_reporting_date',
    'Settle / Pay Date': 'settle_pay_date',
    'Tax Code': 'tax_code',
    'Transaction Type Code': 'transaction_type_code',
    'Transaction Type': 'transaction_type',
    'Main Transaction Code': 'main_transaction_code',
    'Sub Transaction Code': 'sub_transaction_code',
    'Detailed Transaction Type Name': 'detailed_transaction_type_name',
    'Transaction Description 1': 'transaction_description_1',
    'Transaction Description 3': 'transaction_description_3',
    'Transaction Description 4': 'transaction_description_4',
    'Transaction Description 5': 'transaction_description_5',
    'Actual Settle Date': 'actual_settle_date',
    'Alternate Delivery Date': 'alternate_delivery_date',
    'Record Date': 'record_date',
    'Cash Post Date': 'cash_post_date',
    'Cash Value Date': 'cash_value_date',
    'Shares / Par': 'shares_par',
    'Opening Balance Local': 'opening_balance_local',
    'Transaction Amount Local': 'transaction_amount_local',
    'Closing Balance Local': 'closing_balance_local',
    'Transaction Amount Reporting Equivalent': 'transaction_amount_reporting_equivalent',
    'Begin Date': 'begin_date',
    'End Date': 'end_date',
    'Report Run Date': 'report_run_date',
    'Report Run Time': 'report_run_time',
    'Current Factor': 'current_factor',
    'Previous Factor': 'previous_factor',
    'Event ID': 'event_id',
    'Flat Tax %': 'flat_tax_percent',
    'Flat Tax Amount': 'flat_tax_amount',
    'Solidarity %': 'solidarity_percent',
    'Solidarity Amount': 'solidarity_amount',
    'Flat Tax Currency': 'flat_tax_currency'
}

def connect_to_db():
    """Create a connection to the database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"❌ Database connection error: {e}")
        sys.exit(1)

def modify_table_schema(conn, table_name):
    """Modify database schema to handle all data types for a specific table."""
    cursor = conn.cursor()
    
    try:
        # Update ALL columns in table to TEXT
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND column_name != 'id'
        """)
        
        table_columns = cursor.fetchall()
        for col, datatype, nullable in table_columns:
            # Skip already TEXT columns
            if datatype.lower() != 'text':
                print(f"  Converting {table_name}.{col} to TEXT type")
                cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN {col} TYPE TEXT USING {col}::TEXT")
            
            # Make nullable
            if nullable == 'NO':
                print(f"  Making {table_name}.{col} nullable")
                cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN {col} DROP NOT NULL")
        
        conn.commit()
        print(f"✅ Schema for {table_name} modified successfully")
    
    except Exception as e:
        conn.rollback()
        print(f"❌ Error modifying schema for {table_name}: {e}")
        raise
    finally:
        cursor.close()

def clean_dataframe(df, column_map):
    """Process data for import."""
    # Step 1: Drop unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Step 2: Apply column mapping
    df_renamed = pd.DataFrame()
    found_columns = {}
    
    # Track which columns we find and which we don't
    for csv_col, db_col in column_map.items():
        if csv_col in df.columns:
            df_renamed[db_col] = df[csv_col]
            found_columns[csv_col] = True
        else:
            found_columns[csv_col] = False
    
    # Report on column mapping
    print("\nColumn mapping results:")
    for csv_col, found in found_columns.items():
        status = "✅ Found" if found else "❌ Missing"
        print(f"  {status}: {csv_col} → {column_map[csv_col]}")
    
    # Step 3: Clean data values
    for col in df_renamed.columns:
        # Convert to string and clean
        df_renamed[col] = df_renamed[col].astype(str)
        
        # Clean commas from numeric strings
        if col in ['td_amount', 'sd_amount', 'recon_amount', 'ad_amount', 
                   'transaction_amount_local', 'opening_balance_local', 
                   'closing_balance_local', 'transaction_amount_reporting_equivalent',
                   'flat_tax_amount', 'solidarity_amount']:
            df_renamed[col] = df_renamed[col].apply(
                lambda x: x.replace(',', '') if isinstance(x, str) and ',' in x else x
            )
        
        # Replace NaN, None, 'nan', 'NaT' with empty string
        df_renamed[col] = df_renamed[col].replace(['nan', 'NaN', 'NaT', 'None'], '')
    
    return df_renamed

def get_db_columns(conn, table_name):
    """Get column names from a database table."""
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND column_name != 'id'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        return columns
    finally:
        cursor.close()

def insert_data(conn, df, table_name):
    """Insert data into database."""
    cursor = conn.cursor()
    rows_inserted = 0
    
    try:
        # Get database columns
        db_columns = get_db_columns(conn, table_name)
        print(f"Database columns: {len(db_columns)}")
        print(f"DataFrame columns: {len(df.columns)}")
        
        # Check columns match
        missing_cols = [col for col in db_columns if col not in df.columns]
        extra_cols = [col for col in df.columns if col not in db_columns]
        
        if missing_cols:
            print(f"Missing columns in dataframe: {missing_cols}")
        if extra_cols:
            print(f"Extra columns in dataframe: {extra_cols}")
            
        # Filter to only include valid columns
        df_filtered = df[[col for col in df.columns if col in db_columns]]
        
        # Insert each row
        for i, row in df_filtered.iterrows():
            # Skip completely empty rows
            if row.isnull().all():
                continue
                
            # Build column lists and values
            values = []
            columns = []
            
            for col, val in row.items():
                # Skip empty or NaN values
                if pd.isna(val) or val == '':
                    continue
                    
                columns.append(col)
                # Escape single quotes in string values
                if isinstance(val, str):
                    val = val.replace("'", "''")
                values.append(f"'{val}'")
            
            # Skip if no valid columns
            if not columns:
                continue
                
            # Build SQL statement
            column_str = ', '.join([f'"{col}"' for col in columns])
            value_str = ', '.join(values)
            
            sql = f'INSERT INTO {table_name} ({column_str}) VALUES ({value_str})'
            
            try:
                cursor.execute(sql)
                rows_inserted += 1
                
                if rows_inserted % 5 == 0:
                    conn.commit()
                    print(f"✓ {rows_inserted} rows inserted into {table_name}")
                    
            except Exception as e:
                conn.rollback()
                print(f"❌ Error on row {i} for {table_name}: {e}")
                print(f"SQL: {sql[:200]}...")
        
        # Final commit
        conn.commit()
        return rows_inserted
    
    finally:
        cursor.close()

def main():
    print(f"📊 Starting Data Import Process")
    
    try:
        # Connect to the database
        conn = connect_to_db()
        print("✅ Connected to database")
        
        # Process GENEVA table
        print("\n🏦 Processing GENEVA data...")
        modify_table_schema(conn, 'geneva')
        
        print(f"📖 Reading Geneva CSV file...")
        geneva_df = pd.read_csv(GENEVA_CSV)
        print(f"📝 Geneva CSV: {geneva_df.shape[0]} rows, {geneva_df.shape[1]} columns")
        
        print("🧹 Processing Geneva data...")
        geneva_processed = clean_dataframe(geneva_df, GENEVA_COLUMN_MAP)
        
        print("🗑️ Clearing existing Geneva data...")
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE geneva RESTART IDENTITY")
        conn.commit()
        cursor.close()
        
        print("📥 Inserting data into geneva table...")
        geneva_inserted = insert_data(conn, geneva_processed, 'geneva')
        
        # Process CUSTODIAN BANK table
        print("\n🏦 Processing CUSTODIAN BANK data...")
        modify_table_schema(conn, 'custodian_bank')
        
        print(f"📖 Reading Custodian Bank CSV file...")
        custodian_df = pd.read_csv(CUSTODIAN_CSV)
        print(f"📝 Custodian Bank CSV: {custodian_df.shape[0]} rows, {custodian_df.shape[1]} columns")
        
        print("🧹 Processing Custodian Bank data...")
        custodian_processed = clean_dataframe(custodian_df, CUSTODIAN_COLUMN_MAP)
        
        print("🗑️ Clearing existing Custodian Bank data...")
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE custodian_bank RESTART IDENTITY")
        conn.commit()
        cursor.close()
        
        print("📥 Inserting data into custodian_bank table...")
        custodian_inserted = insert_data(conn, custodian_processed, 'custodian_bank')
        
        # Report results
        print("\n📊 Import Results:")
        print(f"✅ Geneva table: {geneva_inserted} rows inserted")
        print(f"✅ Custodian Bank table: {custodian_inserted} rows inserted")
        print("✨ Import completed successfully!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    main()