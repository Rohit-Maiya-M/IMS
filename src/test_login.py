import mysql.connector
from config import DB_CONFIG # Ensure this points to your config

def test_login(email, password):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        # Call the procedure directly
        cursor.callproc('sp_authenticate', [email, password])
        
        # Get the result
        result = None
        for r in cursor.stored_results():
            result = r.fetchone()
        
        print(f"Result for {email}: {result}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

test_login('admin@ims.local', 'password123')