import mysql.connector
from fastapi import FastAPI, Header, HTTPException, Depends, Body
from apiKeys import validate_api_key, generate_api_key, deactivate_api_key, close_connection

app = FastAPI()

db_connection = mysql.connector.connect(
    host="localhost",
    user="",
    password="",
    database="workerapi1"
)
db_cursor = db_connection.cursor()

# Dependency to validate API key
async def validate_api_key_header(api_key: str = Header(...)):
    valid_result = validate_api_key(api_key)
    if not valid_result or not valid_result["is_active"]:
        raise HTTPException(status_code=403, detail="Invalid or inactive API Key")
    return valid_result["username"]

# Endpoint to generate API key for a user
@app.post("/api-key/")
def generate_api_key_endpoint(username: str):
    api_key = generate_api_key(username)
    return {"api_key": api_key}

# Secure endpoint requiring valid API key
@app.get("/secure-data/")
def get_secure_data(username: str = Depends(validate_api_key_header)):
    return {"data": "Sensitive information"}

# for posting comments
@app.post("/comments/")
def create_comment(comment: str = Body(...), username: str = Depends(validate_api_key_header)):
    try:
        # Sanitize inputs to prevent SQL injection (alternative approach)
        sanitized_comment = comment.replace("'", "''")  # Example simple sanitization
        sql = "INSERT INTO comments (username, comment) VALUES (%s, %s)"
        val = (username, sanitized_comment)
        db_cursor.execute(sql, val)
        db_connection.commit()
        return {"message": "Comment posted successfully"}
    except Exception as e:
        print(f"Error creating comment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create comment")

# for editing comments
@app.put("/comments/{comment_id}")
def edit_comment(comment_id: int, comment: str = Body(...), username: str = Depends(validate_api_key_header)):
    try:
        # Sanitize inputs to prevent SQL injection (not necessary with parameterized queries)
        cursor = db_connection.cursor()
        sql = "UPDATE comments SET comment = %s WHERE id = %s AND username = %s"
        val = (comment, comment_id, username)
        cursor.execute(sql, val)
        db_connection.commit()
        cursor.close()  # Close cursor after use
        return {"message": "Comment edited successfully"}
    except mysql.connector.Error as e:
        print(f"Error editing comment: {e.msg}")
        raise HTTPException(status_code=500, detail="Failed to edit comment")

# for deleting comments
@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, username: str = Depends(validate_api_key_header)):
    try:
        sql = "DELETE FROM comments WHERE id = %s AND username = %s"
        val = (comment_id, username)
        db_cursor.execute(sql, val)
        db_connection.commit()
        return {"message": "Comment deleted successfully"}
    except mysql.connector.Error as e:
        print(f"Error deleting comment: {e.msg}")
        raise HTTPException(status_code=500, detail="Failed to delete comment")

@app.on_event("shutdown")
def shutdown_event():
    close_connection()
