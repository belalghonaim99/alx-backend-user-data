#!/usr/bin/env python3
"""Filtered logger module."""
import os
import re
import logging
import mysql.connector
from typing import List


fieldPatterns = {
    'extract': lambda x, y: r'(?P<field>{})=[^{}]*'.format('|'.join(x), y),
    'replace': lambda x: r'\g<field>={}'.format(x),
}
PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(
        fields: List[str], redaction: str, message: str, separator: str,
        ) -> str:
    """Returns a log message with the PII redacted."""
    parseFields, replace = (fieldPatterns["extract"], fieldPatterns["replace"])
    return re.sub(parseFields(fields, separator), replace(redaction), message)


def get_logger() -> logging.Logger:
    """Creates a logger object.
    """
    userDataLogger = logging.getLogger("user_data")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(RedactingFormatter(PII_FIELDS))
    userDataLogger.setLevel(logging.INFO)
    userDataLogger.propagate = False
    userDataLogger.addHandler(console_handler)
    return userDataLogger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Connects to the database.
    """
    databaseHost = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    dbName = os.getenv("PERSONAL_DATA_DB_NAME", "")
    dbUsername = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    db_password = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    db_connection = mysql.connector.connect(
        host=databaseHost,
        port=3306,
        user=dbUsername,
        password=db_password,
        database=dbName,
    )
    return db_connection


def main():
    """Main function of the script.
    """
    fields = "name,email,phone,ssn,password,ip,last_login,user_agent"
    columns = fields.split(',')
    query = "SELECT {} FROM users;".format(fields)
    dataLogger = get_logger()
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            record = map(
                lambda x: '{}={}'.format(x[0], x[1]),
                zip(columns, row),
            )
            fmat_msg = '{};'.format('; '.join(list(record)))
            log = ("user_data", logging.INFO, None, None, fmat_msg, None, None)
            log_record = logging.LogRecord(*log)
            dataLogger.handle(log_record)


class RedactingFormatter(logging.Formatter):
    """Redacting formatter class.
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    FORMAT_FIELDS = ('name', 'levelname', 'asctime', 'message')
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """Filters values from the log record
        """
        format_Mesge = super(RedactingFormatter, self).format(record)
        txt = filter_datum(self.fields, self.REDACTION, format_Mesge, self.SEPARATOR)
        return txt


if __name__ == "__main__":
    main()
