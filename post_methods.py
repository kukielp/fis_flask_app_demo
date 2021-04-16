import psycopg2
from util import get_conn
import json


def insert_vendor(vendor):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO vendors(vendor_name) VALUES(%s) RETURNING vendor_id;", (vendor,))
        vendor_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return json.dumps(vendor_id)