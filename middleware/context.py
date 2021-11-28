import os
import pymysql


def get_db_info():
    """
    :return: A dictionary with connect info for MySQL
    """
    db_host = os.environ.get("DBHOST", None)
    db_user = os.environ.get("DBUSER", None)
    db_password = os.environ.get("DBPASSWORD", None)

    if any(value is None for value in [db_host, db_user, db_password]):
        print(
            "Please ensure DBHOST, DBUSER, and DBPASSWORD environmental variables are set"
        )
        exit(1)

    return {
        "host": db_host,
        "user": db_user,
        "password": db_password,
        "cursorclass": pymysql.cursors.DictCursor,
    }
