import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db/habits_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False