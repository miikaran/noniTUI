from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from psycopg2 import connect

class SQLInterface:
    """Interface for interacting with a PostgreSQL and generating dynamic queries"""
    def __init__(self, db_conn):
        self.conn = db_conn
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        self.table = None
        self.columns = []
        self.clauses = {}
    
    def set_table(self, table):
        self.table = table

    def set_columns(self, columns):
        self.columns = columns

    def set_clauses(self, clauses):
        self.clauses = clauses
    
    def get_table(self):
        return self.table

    def get_columns(self):
        return self.columns
    
    def get_clauses(self):
        return self.clauses

    def init_db_conn(db_credentials):
        return connect(**db_credentials)
    
    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print("Error executing query." + e)
    
    def get_next_serial_id_val(self, serial_col):
        seq = f"{self.table}_{serial_col}_seq"
        self.execute_query(sql.SQL("SELECT nextval({sequence})").format(
                sequence=sql.Literal(seq)
            ))
        return self.cursor.fetchall()[0]["nextval"]
    
    def sort_row_values_by_columns(self, data):
        # Sorts keypairs to match the table col order
        return {key: data[key] for key, type in self.columns}

    def create_query_params(self, params):
        query_params = []
        params_len = len(params)
        for i, param in enumerate(params):
            col = param.get("col")
            clause = param.get("clause")
            value = param.get("value")
            operator = param.get("operator", " AND ")
            if clause in self.clauses.keys():
                used_clause = sql.SQL(self.clauses.get(clause)).format(
                    sql.Identifier(col),
                    sql.Literal(value)
                )
                query_params.append(used_clause)
            if params_len==1 or i==params_len-1:
                continue
            query_params.append(sql.SQL(operator))
        return sql.SQL("").join(query_params)

    def create_format_params(self):
        return {
            "columns": sql.SQL(", ").join(sql.Identifier(col) for col, type in self.columns),
            "table": sql.Identifier(self.table)
        }

    def validate_value_types(self, values):
        for row in values:
            for i, value in enumerate(row):
                target_col = self.columns[i]
                if not target_col:
                    continue
                target_type = target_col[1]
                if not isinstance(value, target_type):
                    print(f"TABLE: {self.table} - Invalid type {type(value)} for col {target_col[0]}. {target_col[1]} required")
                    return False
        return True

    def insert(self, values, returning=""):
        params = self.create_format_params()
        values_list = []
        for row in values:
            print(row)
            if not (self.validate_value_types(values)):
                print(f"TABLE: {self.table} - datatypes not valid for insert: {row}")
                continue
            row_sql = sql.SQL(", ").join(sql.Literal(value) for value in row)
            values_list.append(sql.SQL("({})").format(row_sql))
        params.update({"values": sql.SQL(", ").join(values_list)})
        params.update({"col": sql.Identifier(returning)})
        query = sql.SQL("INSERT INTO {table} ({columns}) values {values} RETURNING {col}").format(
            **params
        )
        print("EXEUCTING:", query.as_string(self.conn))
        self.execute_query(query)
        id = self.cursor.fetchall()[0][returning]
        print(id)
        return True, self.cursor.rowcount, id
    
    def select(self, params, all=False):
        if all == True:
            all_query = sql.SQL("SELECT * FROM {table}").format(
                table=sql.Identifier(self.table)
            )
            self.execute_query(all_query)
            return self.cursor.fetchall()
        format_params = self.create_format_params()
        query_params = self.create_query_params(params)
        format_params.update({"clauses": query_params})
        query = sql.SQL("SELECT {columns} FROM {table} WHERE {clauses}").format(
            **format_params
        )
        print("EXEUCTING:", query.as_string(self.conn))
        self.execute_query(query)
        data = self.cursor.fetchall()
        return data
    
    def update(self, params):
        params.update({"clauses": self.create_query_params(params.get("clauses"))})
        params.update({"table": sql.Identifier(self.table)})
        columns_list = []
        for col, value in params.get("columns").items():
            row_sql = sql.SQL("{}={}").format(
                sql.Identifier(col),
                sql.Literal(value)
            )
            columns_list.append(row_sql)
        params.update({"column_values": sql.SQL(", ").join(columns_list)})
        query = sql.SQL("UPDATE {table} SET {column_values} WHERE {clauses}").format(
            **params
        )
        print("EXEUCTING:", query.as_string(self.conn))
        self.execute_query(query)
        return True, self.cursor.rowcount

    def delete(self, params):
        params.update({"clauses": self.create_query_params(params.get("clauses"))})
        target_table = self.table
        query = sql.SQL("DELETE FROM {table} WHERE {clauses}").format(
            **params,
            table=target_table
        )
        print("EXEUCTING:", query.as_string(self.conn))
        self.execute_query(query)
        return True, self.cursor.rowcount

    def already_exists(self, filter_params):
        query_result = self.select(params=[{
            **filter_params
        }])
        return len(query_result) > 0