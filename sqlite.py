import sqlite3
from prettytable import PrettyTable


def sql_result_to_table_str(sql_result,cursor):
    # Create a PrettyTable object
    table = PrettyTable()
    table.field_names = [description[0] for description in cursor.description]

    # Add rows to the table
    for row in sql_result:
        table.add_row(row)
    table.float_format = ".2"
    return str(table)


class SQLiteDB(object):
    def __init__(self, db_path, user=None, password=None):
        self.db_path = db_path
        self.user = user
        self.password = password
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_sql(self, sql, raise_err=False):
        try:
            # self.connect()
            cursor = None
            for sub_sql in sql.split(";"):
                sub_sql = sub_sql.strip()
                if len(sub_sql) > 0:
                    self.cursor.execute(sub_sql)
            result = self.cursor.fetchall()
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            error_message = f"SQL error: {str(e)}"
            if raise_err:
                raise e
            else:
                return e, error_message
        # finally:
        #     self.disconnect()

        # convert query result to string
        if result:
            out_str = sql_result_to_table_str(result,self.cursor)
        else:
            if "create" in sql.lower():
                out_str = "create table successfully."
            elif "insert" in sql.lower():
                out_str = "insert data successfully."
            elif "delete" in sql.lower():
                out_str = "delete data successfully."
            elif "update" in sql.lower():
                out_str = "update data successfully."
            else:
                out_str = "no results found."

        return result, out_str

    def select(self, table, columns="*", condition=None):
        sql = f"SELECT {columns} FROM {table}"
        if condition:
            sql += f" WHERE {condition}"
        return self.execute_sql(sql)

    def insert(self, table, data):
        keys = ','.join(data.keys())
        values = ','.join([f"'{v}'" for v in data.values()])
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        return self.execute_sql(sql)

    def update(self, table, data, condition):
        set_values = ','.join([f"{k}='{v}'" for k, v in data.items()])
        sql = f"UPDATE {table} SET {set_values} WHERE {condition}"
        return self.execute_sql(sql)

    def delete(self, table, condition):
        sql = f"DELETE FROM {table} WHERE {condition}"
        return self.execute_sql(sql)


if __name__ == '__main__':
    from config import cfg
    sqlite = SQLiteDB(db_path=cfg.sqlite_db_path)
