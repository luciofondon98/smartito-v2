# Add these imports at the top of the file
from sqlalchemy import create_engine, text

def get_database_connection():
    """
    Creates and returns a database connection using SQLAlchemy.
    """
    db_url = "postgresql+psycopg2://postgres:Picopico123@localhost:5432/postgres"
    return create_engine(db_url)