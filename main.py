from fastapi import FastAPI, Header, HTTPException, Depends, Body
from apiKeys import validate_api_key, generate_api_key, deactivate_api_key, close_connection

app = FastAPI()

# Dependency to validate API key
def validate_api_key_header(api_key: str = Header(...)):
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
    # Sanitize inputs to prevent SQL injection
    sanitized_comment = mysql.connector.conversion.MySQLConverter.escape_string(comment)
    sql = "INSERT INTO comments (username, comment) VALUES (%s, %s)"
    val = (username, sanitized_comment)
    db_cursor.execute(sql, val)
    db_connection.commit()
    return {"message": "Comment posted successfully"}

# for editing comments
@app.put("/comments/{comment_id}")
def update_comment(comment_id: int, comment: str = Body(...), username: str = Depends(validate_api_key_header)):
    # Sanitize inputs to prevent SQL injection
    sanitized_comment = mysql.connector.conversion.MySQLConverter.escape_string(comment)
    sql = "UPDATE comments SET comment = %s WHERE id = %s AND username = %s"
    val = (sanitized_comment, comment_id, username)
    db_cursor.execute(sql, val)
    db_connection.commit()
    return {"message": "Comment edited successfully"}

# for deleting comments
@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, username: str = Depends(validate_api_key_header)):
    sql = "DELETE FROM comments WHERE id = %s AND username = %s"
    val = (comment_id, username)
    db_cursor.execute(sql, val)
    db_connection.commit()
    return {"message": "Comment deleted successfully"}

@app.on_event("shutdown")
def shutdown_event():
    close_connection()
