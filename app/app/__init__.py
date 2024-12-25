from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = "IAWODHAWD"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/flidb?charset=utf8mb4" % quote("rooney1403")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

login = LoginManager(app)
db = SQLAlchemy(app)