from argparse import ArgumentError
from flask_bcrypt import Bcrypt
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
#from flask_admin import Admin
from flask_limiter import Limiter
# from flask_session import Session


app = Flask(__name__)



app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Session(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:Password@localhost/PrintAi'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ano:1964#British@localhost/printaiapp'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sam:ksam8657@localhost/sai'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:toor@localhost/printaiapp'


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
limiter = Limiter(app, default_limits=["10000 per minute", "50000000 per hour"])


app.config['SECRET_KEY']= '88d981b544da6ddbfbb1b967'

login_manager.login_view="login_page"
login_manager.login_message_category="info"


from printaiapp import routes
