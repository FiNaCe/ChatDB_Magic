import os
import re
import pandas as pd
from config import cfg
from mysql import MySQLDB
# from fruit_shop_schema import tables
from table_schema import tables
from sqlite import SQLiteDB


def get_table_info(create_table_sql):
    # Regex to match 'CREATE TABLE' followed by the table name
    pattern = r"CREATE TABLE (\w+)"
    match = re.search(pattern, create_table_sql, re.IGNORECASE)
    table_name = match.group(1)

    # Regex to match the column definitions starting with a lowercase letter
    # This pattern matches a word at the start of the line, followed by a space, followed by another word
    pattern = r"^\s*([a-z]\w*)\s+(\w+)"
    matches = re.findall(pattern, create_table_sql, re.MULTILINE)

    # The matches list now contains tuples with the column name and data type
    column_names = []
    column_types = []
    for column_name, data_type in matches:
        column_names.append(column_name)
        column_types.append(data_type)

    return table_name, column_names, column_types


def get_database_info(tables):
    database_info = dict()
    for tab in tables:
        table_name, column_names, column_types = get_table_info(tab)
        database_info[table_name] = {
            "column_names": column_names,
            "column_types": column_types,
        }
    return database_info


database_info = get_database_info(tables)
table_details = "\n".join(tables)


def init_database(database_info, db_name, init_db=True):
    db_type = os.getenv("DB_TYPE", "sqlite")
    print(f"db_type:{db_type}")
    if db_type == 'mysql':
        db = MySQLDB(host=cfg.mysql_host, user=cfg.mysql_user, password=cfg.mysql_password,
                     port=cfg.mysql_port, database=None)
        db.create_database(db_name)
        # create database engine
        from sqlalchemy import create_engine
        from urllib.parse import quote
        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                               .format(user=cfg.mysql_user,
                                       pw=quote(cfg.mysql_password),
                                       host=cfg.mysql_host,
                                       db=db_name))
    else:
        db_path = f"{db_name}.db"
        db = SQLiteDB(db_path=db_path, user=cfg.mysql_user, password=cfg.mysql_password)
        db.connect()
        engine = db.conn

    # read csv data
    if init_db:
        for tab_crate_cmd in tables:
            db.execute_sql(tab_crate_cmd)

        for tab_name in database_info.keys():
            df = pd.read_csv(f'csvs/{tab_name}.csv')
            # write data to MySQL database
            df.to_sql(tab_name, con=engine, if_exists='append', index=False)
    return db


if __name__ == '__main__':
    print(database_info)
    print(table_details)
    # test_db_name = "try1024"
    # init_database(database_info, test_db_name)
