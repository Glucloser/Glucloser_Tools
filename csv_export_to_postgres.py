"""
Fetches a CSV export from Carelink and inserts it into Postgres
"""

import csv
from datetime import date, timedelta
import Carelink
import psycopg2

def slug(val):
    """
    Slugifies strings for postgres
    """
    val = val.replace(" ", "_").replace("-", "_")
    val = val.replace("(", "_").replace(")", "_").replace(":", "_").replace("/", "_")
    return val

def default_for(col_type):
    """
    Returns the default value for the column type
    """

    if col_type == "bigint":
        return -1
    elif col_type == "date":
        return None
    elif col_type == "time":
        return None
    elif col_type == "float":
        return -1.0
    elif col_type == "varchar":
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



    sess = Carelink.startSession()
    Carelink.login(sess, "", "")

    strf_format = "%m/%d/%Y"
    export_start_date = (date.today() - timedelta(days=1)).strftime(strf_format)
    export_end_date = date.today().strftime(strf_format)
    csv_data = Carelink.csv_export(sess, export_start_date, export_end_date)

    csv_reader = csv.reader(csv_data.split("\n"))

    # Skip preamble
    for _ in range(11):
        csv_reader.next()

    headers = map(slug, csv_reader.next())
    header_values = ",".join(headers)


    db_sess = psycopg2.connect(
        "dbname=postgres user=postgres password=test port=32768 host=127.0.0.1")
    with db_sess:
        db_curr = db_sess.cursor()
        insert_count = 0
        for row in csv_reader:
            if len(row) == 0:
                continue

            insert_values = row
            for iv_idx, inval in enumerate(row):
                default = default_for(column_types[iv_idx])
                if inval == "" or inval == '':
                    insert_values[iv_idx] = default

            val_format = ",".join(["%s"] * len(column_types))
            db_curr.execute("INSERT INTO carelink_dump ({}) VALUES ({})".format(
                header_values, val_format), insert_values)
            status = db_curr.statusmessage.split(" ")
            if len(status) != 3:
                print "Insert error: {}".format(db_curr.statusmessage)
            else:
                insert_count += 1

        db_curr.close()
        print "Inserted {} rows".format(insert_count)
    db_sess.close()

if __name__ == "__main__":
    work()
