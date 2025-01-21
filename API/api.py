import flask
from flask import request, render_template
from flask_mysqldb import MySQL
from flask_login import LoginManager
from multiprocessing import Value
from datetime import datetime
from markupsafe import Markup
import requests
import numpy as np
from plots import PlotWeatherData as pwd
from form import LoginForm
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = b'\xb9\xed\xec\xec\x82\x82^YF(5\xd4\xd6P\xb7>'

#Konfiguration MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Haltsmaul-1508'
app.config['MYSQL_DB'] = 'Beet_Daten'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://' + app.config['MYSQL_USER'] + ':' + app.config['MYSQL_PASSWORD'] + '@' + app.config['MYSQL_HOST'] + '/' + app.config['MYSQL_DB']

db.init_app(app)

counter = Value('i', 0)

mysql = MySQL(app)

@app.route('/', methods=['GET'])
def home():
	with counter.get_lock():
		counter.value += 1
		out = counter.value

	now = datetime.now()
	timestring = now.strftime("%Y-%m-%d %H:%M:%S")
	cur = mysql.connection.cursor()
	cur.execute("INSERT INTO Sensordaten (cid, temperature, watercontainerdistance, soilhumidity, airhumidity, airpressure, raindrop, light, time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (1, request.args.get('t'), request.args.get('wcd'), request.args.get('sh'), request.args.get('ah'), request.args.get('p'), request.args.get('rd'), request.args.get('l'), timestring))
	mysql.connection.commit()
	cur.close()

	return "Das ist Anfrage Nummer " + str(out) + " Wert: " + request.args.get('t')



@app.route('/printplots', methods = ['GET'])
def printPlots():

	pwdObject = pwd(int(request.args.get('width')), int(request.args.get('height')), int(request.args.get('dpi')))


	cur = mysql.connection.cursor()
	cur.execute("SELECT temperature, time FROM Sensordaten WHERE time BETWEEN '" + str(request.args.get('from')) + "' AND '" + str(request.args.get('to')) + "'")
	data = np.array(cur.fetchall())
	data = data.transpose()

	cur.close()

	pwdObject.setMarker('-')
	pwdObject.setData(data[1], data[0], 'Temperatur', 'Datum')

	return pwdObject.createHtmlObject()


@app.route('/test', methods = ['GET'])
def test():
	plot_temperature_data = getPlotFromURL('http://192.168.0.241:5000/printplots?width=1200&height=400&dpi=96&from=2021-04-07 00:00&to=2021-04-10 20:00')
	#plot1 = plot1 + requests.get('http://192.168.0.241:5000/printplots?width=300&height=400&dpi=96').content

	return render_template("index.html", plot_temperature = plot_temperature_data)


def getPlotFromURL(url):
	plotData = requests.get(url).content
	plotData = plotData.decode('UTF_8')
	plotData = Markup(plotData)
	return plotData

app.run(host="192.168.178.27") 

#Server beenden Mac:
#sudo lsof -i:5000
#sudo kill [2. Wert]