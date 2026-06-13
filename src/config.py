"""Database connection configuration for IMS."""

import os
from dotenv import load_dotenv

# This line tells Python to find the .env file in your project folder
load_dotenv() 

DB_CONFIG = {
    "host": os.getenv("IMS_DB_HOST", "localhost"),
    "port": int(os.getenv("IMS_DB_PORT", "3306")),
    "user": os.getenv("IMS_DB_USER", "root"),
    "password": os.getenv("IMS_DB_PASSWORD", "maiya@2006"), # Now it will find 'maiya@2006'
    "database": os.getenv("IMS_DB_NAME", "ims_db"),
    "autocommit": True,
}