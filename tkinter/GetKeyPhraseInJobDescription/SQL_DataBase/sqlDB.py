import sqlite3


# -----------------------------------------------------------------------------------------------
def make_connection(db):
    conn = sqlite3.connect(f'{db}.db')
    # Create a cursor object
    cursor = conn.cursor()
    return conn, cursor
def return_condition_rule_from_str(column_str):
    """
        Parse a column string to extract the condition rule and column name.

        This function interprets suffix markers in a column string to decide
        how the condition should be built when generating SQL queries.
        Supported suffixes:
          - "__contains" → substring match (SQL LIKE)
          - "__operator" → comparison operator (>, <, >=, <=, =)

        Parameters
        ----------
        column_str : str
            The column string, possibly including a rule suffix.
            Examples: "name__contains", "age__operator", "status".

        Returns
        -------
        tuple
            (condition_rule, column_name)
            - condition_rule : str
                One of {"contains", "operator", ""}.
            - column_name : str
                The actual column name without the suffix.

        Example
        -------
        >> return_condition_rule_from_str("name__contains")
        ("contains", "name")

        >> return_condition_rule_from_str("age__operator")
        ("operator", "age")

        >> return_condition_rule_from_str("status")
        ("", "status")
    """
    condition_rule = ''
    list_key_splited = column_str.split('__')
    if 'contains' in list_key_splited:
        condition_rule = 'contains'
    elif 'operator' in list_key_splited:
        condition_rule = 'operator'
    return condition_rule,list_key_splited[0]
def create_query_by_colValue_relatedCol_condition(related_col='and',**col_values):
    """
    Build a dynamic SQL WHERE clause and parameter list from column filters.

    This helper function constructs conditional expressions based on
    naming conventions in the provided keyword arguments. It returns
    both the WHERE clause string (without the leading "WHERE") and
    a list of parameters for safe use in parameterized queries.

    Parameters
    ----------
    related_col : str, default='and'
        Logical connector between conditions ("and" or "or").
    **col_values : dict
        Column filters with optional suffix rules:
            - "col=value" → exact match (`col = ?`)
            - "col=[val1, val2]" → IN clause (`col IN (?, ?)`).
            - "col_contains" → substring match:
                  * str → `col LIKE ?` with `%value%`
                  * list[str] → OR-combined LIKE conditions
            - "col_operator=(operator, number)" → comparison operator
                  * operator ∈ {<, >, <=, >=, =}
                  * Example: age_operator=('>', 18) → `age > ?`

    Returns
    -------
    where_clause : str
        SQL condition string ready to be appended after `WHERE`.
    params : list
        List of parameters corresponding to the placeholders in `where_clause`.

    Example
    -------
    >> create_query_by_colValue_relatedCol_condition(
    ...     related_col="and",
    ...     name="Alice",
    ...     age_operator=('>', 25),
    ...     city_contains="York",
    ...     status=["active", "pending"]
    ... )
    # Returns:
    # ("name = ? and age > ? and city LIKE ? and status IN (?, ?)",
    #  ["Alice", 25, "%York%", "active", "pending"])
    """
    list_col_val_str = []
    params = []
    for pre_process_column, value_or_values in col_values.items():
        condition_rule,column = return_condition_rule_from_str(pre_process_column)
        if condition_rule == 'contains':
            if isinstance(value_or_values, list):
                # iterable of value_or_values
                column_conditions = [f"{column} LIKE ?" for _ in value_or_values]
                list_col_val_str.append(f"({' OR '.join(column_conditions)})")
                params.extend([f"%{substring}%" for substring in value_or_values])
            elif isinstance(value_or_values, str):
                # Single substring
                list_col_val_str.append(f"{column} LIKE ?")
                params.append(f"%{value_or_values}%")
        elif condition_rule == 'operator':
            if isinstance(value_or_values, tuple) and len(value_or_values) == 2:
                # Comparison operator and float number
                operator, number = value_or_values
                if operator in ('<', '>', '<=', '>=', '='):
                    list_col_val_str.append(f"{column} {operator} ?")
                    params.append(number)

        else:
            if isinstance(value_or_values, (tuple, list)):
                placeholders = ','.join(['?' for _ in value_or_values])
                list_col_val_str.append(f"{column} IN ({placeholders})")
                params.extend(value_or_values)
            else:
                list_col_val_str.append(f"{column} = ?")
                params.append(value_or_values)
    where_clause = f" {related_col} ".join(list_col_val_str)
    return where_clause ,params

def get_tableName_and_columnsFromDBmaster(db):
    conn, cursor = make_connection(db)

    # Execute the query to find all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Fetch all results
    tables = cursor.fetchall()
    # Dictionary to store tables and their columns
    tables_columns = {}

    # Iterate through the tables and get their columns
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        tables_columns[table_name] = column_names
    # Close the connection
    conn.close()
    return tables_columns


def get_columnsNameFromTable(db, table_name):
    conn, cursor = make_connection(db)
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    conn.close()
    return column_names


def check_table_exists(db, table_name):
    conn, cursor = make_connection(db)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    res = cursor.fetchone() is not None
    conn.close()
    return res
def is_tableNotEmpty(db,table_name):
    conn, cursor = make_connection(db)
    cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1;")
    row = cursor.fetchone()
    conn.close()
    if row:
        return True
    else:
        return False

def update_ColNameType(db, table_name, old_colName, new_col_name, new_col_type):
    """Update a column name and/or type in a database table.

        Args:
            db (str): Database name (without `.db` extension).
            table_name (str): Name of the table to modify.
            old_colName (str): Current column name to be changed.
            new_col_name (str): New column name.
            new_col_type (str): New column data type (e.g., "TEXT", "INTEGER").

        Returns:
            None

        Example:
            >> update_ColNameType("companyDB", "Employees", "job", "position", "TEXT")
        """
    conn, cursor = make_connection(db)
    cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_colName} TO {new_col_name};")
    cursor.execute(f"ALTER TABLE {table_name} MODIFY COLUMN {new_col_name} {new_col_type};")
    conn.commit()
    conn.close()


def drop_table(db, tabel_name):
    conn, cursor = make_connection(db)
    cursor.execute(f"DROP TABLE {tabel_name}")
    conn.commit()
    conn.close()


def table_maker(tabel_name:str, db:str, *args, strick_flag=False):
    """
    Create a new table in a SQLite database.

    By default, the function creates the table only if it does not already exist.
    A primary key column named `id_` (auto-incremented integer) is always created.
    Additional columns can be specified through `*args`.

    Parameters
    ----------
    tabel_name : str
        Name of the table to create.
    db : str
        SQLite database name (without the `.db` extension).
    *args : str
        Column definitions (e.g., "name TEXT", "age INTEGER").
    strick_flag : bool, default=False
        - If False: uses `CREATE TABLE IF NOT EXISTS` (safe creation).
        - If True: uses `CREATE TABLE` (raises an error if the table exists).

    Returns
    -------
    None

    Example
    -------
    >> table_maker("users", "my_database", "name TEXT", "age INTEGER")
    # Creates a table like:
    # CREATE TABLE IF NOT EXISTS users (id_ INTEGER PRIMARY KEY, name TEXT, age INTEGER)

    >> table_maker("logs", "my_database", strick_flag=True)
    # Creates a table with only an auto-increment id_ column.
    """
    conn, cursor = make_connection(db)
    args_str = ""
    for i in args:
        args_str += i + ","
    args_str = args_str[:-1]

    if strick_flag == False:
        if args_str != "":
            cursor.execute(f'create table if not exists {tabel_name} (id_ integer primary key ,{args_str})')
        else:
            cursor.execute(f'create table if not exists {tabel_name} (id_ integer primary key)')
    else:
        if args_str != "":
            cursor.execute(f'create table {tabel_name} (id_ integer primary key ,{args_str})')
        else:
            cursor.execute(f'create table {tabel_name} (id_ integer primary key)')
    conn.commit()
    conn.close()


def insert(tabel_name, db, *args, **kwargs):
    """
    Insert a new row into a SQLite table.

    Supports two insertion modes:
      1. Keyword arguments (column=value) → inserts values into specified columns.
      2. Positional arguments (*args) → inserts values into all columns
         (with `NULL` for the first column, typically an auto-increment ID).

    Parameters
    ----------
    table_name : str
        Name of the table to insert into.
    db : str
        SQLite database name (without the `.db` extension).
    *args : tuple
        Values to insert directly into the table (excluding the first column).
        Used when explicit column names are not provided.
    **kwargs : dict
        Column-value pairs for the insert statement. Columns correspond to keys.

    Returns
    -------
    int
        The `rowid` of the inserted record.

    Example
    -------
    >> insert("users", "my_database", name="Alice", age=30)
    # Executes:
    # INSERT INTO users (name, age) VALUES (?, ?)

    >> insert("users", "my_database", "Alice", 30)
    # Executes:
    # INSERT INTO users VALUES (NULL, ?, ?)
    """

    conn, cursor = make_connection(db)
    if args == ():
        columns = ','.join([col for col in kwargs.keys()])
        args = tuple(kwargs.values())
        ques = ','.join(['?' for _ in args])
        # print(f'insert into {tabel_name} ({columns}) values ({ques})', args)
        cursor.execute(f'insert into {tabel_name} ({columns}) values ({ques})', args)
    else:
        ques = ','.join(['?' for _ in args])
        cursor.execute(f'insert into {tabel_name} values (NULL,{ques})', args)
    last_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return last_id


def delete(table_name, db,related_col='and', **col_values):
    """
        Delete rows from a SQLite table with optional filtering.

        If no filters are provided, all rows are deleted. When filters are
        supplied, they are combined with the specified logical operator
        ("and" or "or") to form the WHERE clause. Returns the IDs of the
        deleted rows.

        Parameters
        ----------
        table_name : str
            Name of the table to delete from.
        db : str
            SQLite database name (without the `.db` extension).
        related_col : str, default='and'
            Logical connector between multiple filter conditions ("and" or "or").
        **col_values : dict
            Column filters for selecting which rows to delete. Uses the same
            format as `create_query_by_colValue_relatedCol_condition`:
                - "col": value → exact match
                - "col": [val1, val2] → IN clause
                - "col_contains": "substring" or ["sub1", "sub2"] → LIKE clause
                - "col_operator": (operator, number) → comparison (e.g., ('>', 10))

        Returns
        -------
        list of int
            The row IDs (`rowid`) of the deleted records.

        Example
        -------
        >> delete("Employees", "companyDB", name="Alice")
            [1]
        >> delete("Employees", "companyDB", age__operator=(">", 40))
            [3, 4, 5]
        >> delete("users", "my_database", name="Alice")
        # Deletes all rows where name = 'Alice' and returns their rowids.

        >> delete("users", "my_database")
        # Deletes all rows in the users table and returns all rowids.
    """
    if col_values == {}:
        conn, cursor = make_connection(db)
        cursor.execute(f"SELECT rowid FROM {table_name}")
        rows_id = cursor.fetchall()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        conn.close()
        return [id_[0] for id_ in rows_id]
    queri , params = create_query_by_colValue_relatedCol_condition(related_col=related_col, **col_values)
    conn, cursor = make_connection(db)
    # print(f"SELECT rowid FROM {table_name} WHERE {queri}",params)
    cursor.execute(f"SELECT rowid FROM {table_name} WHERE {queri}", params)
    rows_id = cursor.fetchall()

    if rows_id is []:
        # No matching row found, nothing to delete
        conn.close()
        return [id_[0] for id_ in rows_id]


    # Perform the deletion
    cursor.execute(f"DELETE FROM {table_name} WHERE {queri}", params)
    conn.commit()
    conn.close()
    return [id_[0] for id_ in rows_id]





def view(table_name, db, sort_by=None,related_col='and',filter_kind='', **col_values):
    """
        Retrieve rows from a SQLite table with optional filtering and sorting.

        Builds a SELECT query dynamically based on provided column filters,
        logical conditions, and sorting rules. Supports equality, containment,
        operators, and multiple values for a column.

        Parameters
        ----------
        table_name : str
            Name of the table to query.
        db : str
            SQLite database name (without the `.db` extension).
        sort_by : str, optional
            Sorting clause (e.g., "ORDER BY age DESC").
        related_col : str, default='and'
            Logical connector between multiple conditions ("and" or "or").
        filter_kind : str, optional
            Reserved for additional filtering modes (not yet implemented).
        **col_values : dict
            Column filters with special rules:
                - "col": value → exact match
                - "col": [val1, val2] → IN clause
                - "col_contains": "substring" or ["sub1", "sub2"] → LIKE clause
                - "col_operator": (operator, number) → comparison (e.g., ('>', 10))

        Returns
        -------
        result : list of tuple
            List of rows that match the query.
        columns : list of str
            Column names from the query result.

        Example
        -------
        >> view("users", "my_database", sort_by="ORDER BY age DESC",
        ...      name="Alice", age_operator=('>', 25))
        # Executes:
        # SELECT * FROM users WHERE name = ? AND age > ? ORDER BY age DESC
        # with params ("Alice", 25)
    """
    search_into_columns = 'WHERE '
    where_clause, params = create_query_by_colValue_relatedCol_condition(related_col=related_col,**col_values)
    search_into_columns += where_clause
    if search_into_columns == 'WHERE ':
        search_into_columns = ''

    if sort_by:
        search_into_columns += f" {sort_by}"


    sql_command = f'SELECT * FROM {table_name} {search_into_columns}'

    conn, cursor = make_connection(db)
    # print(sql_command)  # Debugging line to see the generated SQL command
    cursor.execute(sql_command, params)
    columns = [description[0] for description in cursor.description]
    result = cursor.fetchall()
    conn.close()

    return result, columns



def search(table_name, db,related_col='and', **col_values):
    """
        Search for rows in a table that match specified conditions.

        Args:
            table_name (str): Name of the table to search in.
            db (str): Name of the database (without `.db` extension).
            related_col (str, optional): Logical operator to join conditions.
                Accepts 'and' or 'or'. Default is 'and'.
            **col_values: Column-value pairs to filter the query.
                - Exact match: column=value
                - IN list: column=[v1, v2, v3]
                - Contains: column__contains="substring" or column__contains=["sub1","sub2"]
                - Operator: column__operator=('<', 5) or column__operator=('>=', 10)

        Returns:
            tuple:
                - result (list of tuples): The rows matching the conditions.
                - columns (list of str): The column names of the table.

        Example:
            >> search("employees", "companyDB", Name__contains="John")
            ([('John Smith', 'IT'), ('Johnny Doe', 'HR')], ['Name', 'Department'])
                Example usage:

        # 1. Exact match
        search("employees", "companyDB", Name="Alice")

        # 2. Multiple exact matches (AND by default)
        search("employees", "companyDB", Name="Alice", Department="IT")

        # 3. OR condition
        search("employees", "companyDB", related_col="or", Name="Alice", Department="HR")

        # 4. IN clause
        search("employees", "companyDB", Department=["HR", "Finance"])

        # 5. Contains
        search("employees", "companyDB", Name__contains="Jo")

        # 6. Contains multiple values
        search("employees", "companyDB", Notes__contains=["urgent", "review"])

        # 7. Operator
        search("employees", "companyDB", Age__operator=(">=", 30))

        # 8. Mixed conditions
        search(
            "employees",
            "companyDB",
            related_col="and",
            Department=["IT", "HR"],
            Name__contains="Ali",
            Age__operator=(">", 25)
        )
        """
    where_clause, params = create_query_by_colValue_relatedCol_condition(related_col=related_col, **col_values)
    # print(where_clause, params)
    conn, cursor = make_connection(db)
    # print(f'-- select * from {table_name} where {where_clause} ',tuple(params))
    cursor.execute(f'select * from {table_name} where {where_clause} ', tuple(params))
    columns = [description[0] for description in cursor.description]
    result = cursor.fetchall()
    conn.close()
    return result, columns

def update(db, table_name, condition_str, **kwargs):
    """
        Update rows in a SQLite table with new values.

        This function updates one or more columns in the specified table
        based on the provided condition. Columns with empty string values
        are ignored and not included in the update query.

        Parameters
        ----------
        db : str
            The name of the SQLite database (without the `.db` extension).
        table_name : str
            The name of the table to update.
        condition_str : str
            The WHERE clause condition as a string (e.g., "id = 1").
        **kwargs : dict
            Key-value pairs representing column names and their new values.
            Columns with empty string values are skipped.

        Example
        -------
        >> update("my_database", "users", "id = 5", name="Alice", age=30, email="")
        # This will execute:
        # UPDATE users SET name = ?, age = ? WHERE id = 5
        # with parameters ("Alice", 30)
        """
    queri = ''
    for key, value in kwargs.items():
        if value == '':
            continue
        queri += key + ' = ?' + ', '
    queri = queri[:-2] + ' '
    listlOfValues = []
    for v in kwargs.values():
        if v == '':
            continue
        listlOfValues.append(v)
    tuple_of_values = tuple(listlOfValues)
    # Connect to the SQLite database
    conn, cursor = make_connection(db)
    # Define the SQL statement to add a new column
    query = f"UPDATE {table_name} SET {queri} WHERE {condition_str}"
    # Execute the SQL statement
    cursor.execute(query, tuple_of_values)
    # Commit the changes
    conn.commit()


def add_col(db, table_name, col_name, dType, id='id_'):
    conn, cursor = make_connection(db)
    column_names = get_columnsNameFromTable(db, table_name)
    result = check_col_exist_and_return_col_rows(db, table_name, col_name, column_names, id=id)
    if result:
        pass
    else:
        # Define the SQL statement to add a new column
        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {dType}"
        # Execute the SQL statement
        cursor.execute(alter_query)
        # Commit the changes
        conn.commit()

    # Close the connection
    conn.close()


def check_col_exist_and_return_col_rows(db, table_name, col_name, column_names, id='id_'):
    if col_name in column_names:
        conn, cursor = make_connection(db)
        cursor.execute(f'SELECT {id}, {col_name} FROM {table_name}')
        data = cursor.fetchall()
        conn.close()
        return data
    else:
        return False


def drop_col(db, table_name, col_name):
    conn, cursor = make_connection(db)
    cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {col_name}")
    conn.commit()
    conn.close()
