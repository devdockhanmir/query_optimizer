import pyodbc

def connect_and_query():
    connection_string = (
        "Driver={SQL Server};"
        "Server=Dark/SQLEXPRESS,1433;"  
        "Database=AdventureWorks2022;"  
        "Trusted_Connection=yes;"
    )

    try:
        conn = pyodbc.connect(connection_string)
        print("Connection successful!")

        # Create a cursor and execute a test query
        cursor = conn.cursor()
        test_query = """
        SELECT TOP 5 FirstName, LastName
        FROM Person.Person;
        """
        cursor.execute(test_query)

        # Fetch results
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        # Print the results
        print(columns)
        for row in rows:
            print(row)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close connection
        if 'conn' in locals() and conn:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    connect_and_query()
