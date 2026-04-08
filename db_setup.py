
import psycopg2
import pandas as pd
from config import DB_CONFIG

def get_connection():
   
    return psycopg2.connect(**DB_CONFIG)

def create_table():
   
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS claims;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id                        SERIAL PRIMARY KEY,
            rndrng_prvdr_state_abrvtn VARCHAR(5),
            rndrng_prvdr_city         TEXT,
            rndrng_prvdr_org_name     TEXT,
            drg_cd                    VARCHAR(10),
            drg_desc                  TEXT,
            tot_dschrgs               INTEGER,
            avg_submtd_cvrd_chrg      NUMERIC(12, 2),
            avg_tot_pymt_amt          NUMERIC(12, 2),
            avg_mdcr_pymt_amt         NUMERIC(12, 2)
        );
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_state
        ON claims (rndrng_prvdr_state_abrvtn);
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Table and index created.")

def load_medicare_data():

    print("Reading Medicare CSV file...")
    df = pd.read_csv("medicare_claims.csv", encoding="latin-1")
    
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    columns_needed = [
        "rndrng_prvdr_state_abrvtn",
        "rndrng_prvdr_city",
        "rndrng_prvdr_org_name",
        "drg_cd",
        "drg_desc",
        "tot_dschrgs",
        "avg_submtd_cvrd_chrg",
        "avg_tot_pymt_amt",
        "avg_mdcr_pymt_amt"
    ]
    df = df[columns_needed]

    df = df.dropna(subset=["avg_submtd_cvrd_chrg", "avg_mdcr_pymt_amt"])

    for col in ["tot_dschrgs", "avg_submtd_cvrd_chrg", "avg_tot_pymt_amt", "avg_mdcr_pymt_amt"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()  
    print(f"Cleaned data: {len(df):,} rows ready to insert.")

    conn = get_connection()
    cursor = conn.cursor()

    import io
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    cursor.copy_expert("""
        COPY claims (
            rndrng_prvdr_state_abrvtn,
            rndrng_prvdr_city,
            rndrng_prvdr_org_name,
            drg_cd,
            drg_desc,
            tot_dschrgs,
            avg_submtd_cvrd_chrg,
            avg_tot_pymt_amt,
            avg_mdcr_pymt_amt
        )
        FROM STDIN WITH CSV
    """, buffer)

    conn.commit()
    print(f"Inserted {len(df):,} rows into PostgreSQL.")
    cursor.close()
    conn.close()

def setup():
    create_table()
    load_medicare_data()


if __name__ == "__main__":
    setup()