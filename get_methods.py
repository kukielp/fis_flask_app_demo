import psycopg2
from util import get_conn
from flask import Response

def get_vendors():
    """ query data from the vendors table """
    res = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT vendor_id, vendor_name FROM vendors ORDER BY vendor_name")
        print("The number of parts: ", cur.rowcount)
        res = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return res

def get_vendors_500():
    """ query data from the vendors table """
    res = None
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT vendor_id, vendor_name FROM vendors ORDER BY vendor_name")
    print("The number of parts: ", cur.rowcount)
    res = cur.fetchall()
    cur.close()
    if conn is not None:
            conn.close()
    return res

def get_500_response():
    return Response(
        {'message' : 'error 1005'},
        status=500,
    )
