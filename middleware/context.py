import os
import pymysql


def get_aws_credentials():
    """
    :return: A dictionary with AWS boto credentials for SNS service
    """
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID", None)
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", None)

    if any(value is None for value in [aws_access_key, aws_secret_key]):
        print(
            "Please ensure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environmental variables are set"
        )
        exit(1)

    return {
        "aws_access_key": aws_access_key,
        "aws_secret_key": aws_secret_key
    }


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
