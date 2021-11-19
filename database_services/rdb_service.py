import pymysql
import json
import logging

import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RDBServiceException(Exception):

    def __init__(self, msg):
        self.msg = msg


class InvalidDbRequest(Exception):

    def __init__(self, msg):
        self.msg = msg


def _get_db_connection():

    db_connect_info = context.get_db_info()
    logger.info("rdb_service._get_db_connection:")
    logger.info("\t host = " + db_connect_info["host"])

    db_info = context.get_db_info()
    db_connection = pymysql.connect(**db_info)
    return db_connection


def fetch_all_records(db_schema, table_name):
    conn = _get_db_connection()
    cur = conn.cursor()

    sql = "SELECT * FROM " + db_schema + "." + table_name
    print("sql statement = " + cur.mogrify(sql, None))

    res = cur.execute(sql)
    res = cur.fetchall()
    conn.close()
    return res


def get_by_prefix(db_schema, table_name, column_name, value_prefix):
    conn = _get_db_connection()
    cur = conn.cursor()

    sql = (
        "SELECT * FROM "
        + db_schema
        + "."
        + table_name
        + " WHERE "
        + column_name
        + " LIKE "
        + "'"
        + value_prefix
        + "%'"
    )
    print("SQL Statement = " + cur.mogrify(sql, None))

    res = cur.execute(sql)
    res = cur.fetchall()
    conn.close()
    return res


def _get_where_clause_args(template):

    terms = []
    args = []
    clause = None

    if template is None or template == {}:
        clause = ""
        args = None
    else:
        for k, v in template.items():
            terms.append(k + "=%s")
            args.append(v)

        clause = " WHERE " + " AND ".join(terms)

    return clause, args


def find_by_template(db_schema, table_name, template):
    """
    Find an individual record by SQL template.
    :param db_schema: Schema name
    :param table_name: Table name
    :param template: A dictionary containing key, value pairs representing WHERE statements
    :return: Records found under template
    """
    conn = _get_db_connection()
    cur = conn.cursor()

    where_clause, args = _get_where_clause_args(template)
    sql = "SELECT * FROM " + db_schema + "." + table_name + " " + where_clause

    res = cur.execute(sql, args)
    res = cur.fetchall()
    conn.close()
    return res


def update_record(db_schema, table_name, key_column, key, **kwargs):
    """
    Update a database record with the mapping provided
    :param db_schema: Schema name
    :param table_name: Table name
    :param: key_column: Name of key column
    :param key: The id of the record to update
    :param kwargs: Mapping of column to value to update
    :return: Database record updated, Throws RDBServiceException() if error occurs
    """
    update_elements = [key + " = %s" for key in kwargs.keys()]
    update_sql = ", ".join(update_elements)
    sql = (
        "UPDATE "
        + db_schema + "." + table_name
        + " SET "
        + update_sql
        + " WHERE " + key_column + " = %s"
    )
    args = [v for v in kwargs.values()]
    args.append(key)  # last arg is the item id itself
    return _execute_db_commit_query(sql, args)


def create_new_record(db_schema, table_name, **kwargs):
    """
    Inserts a record into the database generically as a list of key, value arguments.
    :param db_schema: Schema name
    :param table_name: Table name
    :param kwargs: Dictionary of key, value arguments
    :return: Database record created, Throws RDBServiceException() if error occurs
    """
    conn = _get_db_connection()
    cur = conn.cursor()

    columns = [key for key in kwargs.keys()]
    value_placeholders = ["%s" for _ in kwargs.keys()]
    column_specifier = "(" + ", ".join(columns) + ")"
    value_specifier = "(" + ", ".join(value_placeholders) + ")"
    sql = (
        "INSERT INTO "
        + db_schema + "." + table_name
        + column_specifier
        + " VALUES " + value_specifier
    )

    try:
        cur.execute(sql, args=[v for v in kwargs.values()])
        new_row = cur.lastrowid
        conn.commit()
        return new_row
    except Exception as e:
        raise RDBServiceException(e)
    finally:
        conn.close()


def delete_record_by_key(db_schema, table_name, key_column, item_id):
    """
    Deletes a single record from the database table by key; note that key column must be
    specified
    :param db_schema: Database schema name
    :param table_name: Table name
    :param key_column: The column name that contains the table key
    :param item_id: The id of the item to delete
    :return:
    """
    sql = (
        "DELETE FROM " + db_schema + "." + table_name + " WHERE " + key_column + " = %s"
    )
    return _execute_db_commit_query(sql, item_id)


def _execute_db_commit_query(sql, args):
    """
    Function to execute database query, based on provided sql statement
    :param sql: String version of SQL statement to run
    :return: Database response
    """
    conn = _get_db_connection()
    cur = conn.cursor()
    try:
        res = cur.execute(sql, args=args)
        conn.commit()
        return res
    except Exception as e:
        raise RDBServiceException(str(e))
    finally:
        conn.close()

