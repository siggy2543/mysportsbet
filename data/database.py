import mysql.connector

# Database connection
def connect_to_database():
    # Replace the connection details with your MySQL database credentials
    return mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database"
    )

""" # CRUD methods for models
def create_user(user):
    # DB insert 
    pass

def get_user(id):
    # DB select
    pass """
