from flask import Flask
app = Flask(__name__)

app.secret_key = b'SECRET KEY'

app.config["DEBUG"] = True
app.config["HOST_IP"] = "IP ADDRESS"	

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'MYSQL USER'
app.config['MYSQL_PASSWORD'] = 'MYSQL PASSWORD'
app.config['MYSQL_DB'] = 'MYSQL DB'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://' + app.config['MYSQL_USER'] + ':' + app.config['MYSQL_PASSWORD'] + '@' + app.config['MYSQL_HOST'] + '/' + app.config['MYSQL_DB']

from jsonEncoder import MyJSONEncoder
app.json_encoder = MyJSONEncoder

import db 
db.db.init_app(app)

from flask_mysqldb import MySQL
db.mysql = MySQL(app)

from auth import login_manager
login_manager.init_app(app)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from main import main as main_blueprint
app.register_blueprint(main_blueprint)

from data import data as data_blueprint
app.register_blueprint(data_blueprint)

from controller import controller as controller_blueprint
app.register_blueprint(controller_blueprint)

app.run(host=app.config["HOST_IP"]) 

