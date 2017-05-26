"""
Fetches a CSV export from Carelink and inserts it into Postgres
"""

import csv
import re
import Carelink
import dateutil.parser as dtparser
import psycopg2

def slug(val):
    """
    Slugifies strings for postgres
    """
    val = val.replace(" ", "_").replace("-", "_")
    val = val.replace("(", "_").replace(")", "_").replace(":", "_").replace("/", "_")
    return val

def default_for(type):
    if type == "bigint":
        return -1
    elif type == "date":
        return None
    elif type == "time":
        return None
    elif type == "float":
        return -1.0
    elif type == "varchar":
        return ""

def work():
    """
    Fetch a csv data export from Carelink and insert the rows into postgres
    """

    column_types = [
        "bigint",
        "date",
        "time",
        "date",
        "date",
        "int",
        "varchar",
        "float",
        "varchar",
        "time",
        "varchar",
        "float",
        "float",
        "time",
        "varchar",
        "float",
        "varchar",
        "varchar",
        "float",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "float",
        "float",
        "float",
        "varchar",
        "int",
        "int",
        "float",
        "float",
        "varchar",
        "varchar",
        "bigint",
        "bigint",
        "bigint",
        "varchar"
            ]

    db_sess = psycopg2.connect("dbname=postgres user=postgres password=test port=32768 host=127.0.0.1")


    sess = Carelink.startSession()
    Carelink.login(sess, "nil088", "childrensdc")
    csv_data = Carelink.csv_export(sess)

    csv_reader = csv.reader(csv_data.split("\n"))

    # Skip preamble
    for _ in range(12):
        csv_reader.next()

    headers = map(slug, csv_reader.next())


    db_curr = db_sess.cursor()
    for row_idx, row in enumerate(csv_reader):
        if len(row) == 0:
            continue
        header_values = ",".join(headers)

        insert_values = row
        for iv_idx, inval in enumerate(row):
            default = default_for(column_types[iv_idx])
            if inval == "" or inval == '':
                insert_values[iv_idx] = default

        val_format = ",".join(["%s"] * len(column_types))
        db_curr.execute("INSERT INTO carelink_dump ({}) VALUES ({})".format(
            header_values, val_format), insert_values)
        print db_curr.statusmessage

    db_curr.close()
    db_sess.commit()
    db_sess.close()

if __name__ == "__main__":
    work()
