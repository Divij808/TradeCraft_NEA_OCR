import sqlite3

# 1. Connect to the tradecraft database
# Ensure the file path matches your database location (e.g., 'tradecrafts.db')
conn = sqlite3.connect('tradecrafts.db')
cursor = conn.cursor()

try:
    # 2. Define the target email and table name
    target_email = "Mekala.divij@gmail.com"

    # Replace 'users' with your specific table name
    sql_query = "DELETE FROM users WHERE email = ?"

    # 3. Execute the deletion using a tuple for the parameter
    cursor.execute(sql_query, (target_email,))

    # 4. Commit changes to make them permanent
    conn.commit()
    print(f"Successfully deleted {cursor.rowcount} row(s).")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
    conn.rollback()

finally:
    # Always close the connection
    conn.close()
