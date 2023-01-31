from flask import Flask
import os 
import sqlite3
from flask_sqlalchemy import SQLAlchemy


app= Flask(__name__)

file_path=os.path.abspath(os.getcwd())+"/gladys.db"
print(file_path)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+file_path
db=SQLAlchemy(app)


from app import server