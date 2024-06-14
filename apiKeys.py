import uuid
import bcrypt
import mysql.connector

# Connect to MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ant1mama",
    database="workerapi1"
)
db_cursor = db_connection.cursor()

# Function to generate API key
def generate_api_key(username):
    api_key = str(uuid.uuid4())
    hashed_api_key = bcrypt.hashpw(api_key.encode(), bcrypt.gensalt()).decode()
    # Store in database
    sql = "INSERT INTO api_keys (username, api_key) VALUES (%s, %s)"
    val = (username, hashed_api_key)
    db_cursor.execute(sql, val)
    db_connection.commit()
    return api_key

# Function to validate API key
def validate_api_key(api_key):
    sql = "SELECT username, api_key, is_active FROM api_keys WHERE api_key = %s"
    db_cursor.execute(sql, (api_key,))
    result = db_cursor.fetchone()
    if result:
        return {
            "username": result[0],
            "is_active": result[2]
        }
    return None

# Function to deactivate API key
def deactivate_api_key(api_key):
    sql = "UPDATE api_keys SET is_active = FALSE WHERE api_key = %s"
    db_cursor.execute(sql, (api_key,))
    db_connection.commit()

def close_connection():
    if db_cursor:
        db_cursor.close()
    if db_connection:
        db_connection.close()