
import psycopg2
from db_setup import get_connection

def get_top_procedures_by_state(state_code):
   
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            drg_desc,
            SUM(tot_dschrgs)                          AS total_discharges,
            ROUND(AVG(avg_submtd_cvrd_chrg)::numeric, 2) AS avg_billed,
            ROUND(AVG(avg_mdcr_pymt_amt)::numeric, 2)    AS avg_paid
        FROM claims
        WHERE rndrng_prvdr_state_abrvtn = %s
        GROUP BY drg_desc
        ORDER BY total_discharges DESC
        LIMIT 10;
    """, (state_code,))

    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_billing_gap_by_state(state_code):
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            rndrng_prvdr_state_abrvtn                              AS state,
            ROUND(AVG(avg_submtd_cvrd_chrg - avg_mdcr_pymt_amt)::numeric, 2)
                                                                   AS avg_billing_gap,
            COUNT(*)                                               AS claim_count
        FROM claims
        WHERE rndrng_prvdr_state_abrvtn = %s
        GROUP BY state;
    """, (state_code,))

    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result