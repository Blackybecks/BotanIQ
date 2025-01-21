from flask import Blueprint, request, jsonify
from flask_login import login_required
import numpy as np
from datetime import datetime
import pytz
import plots as plt
from db import mysql


data = Blueprint('data', __name__)

@data.route('/plot')
def plot():
	pwdObject = plt.PlotWeatherData(int(request.args.get('width')), int(request.args.get('height')), int(request.args.get('dpi')))

	cur = mysql.connect.cursor()
	cur.execute("SELECT temperature, time FROM Sensordaten"); #WHERE time BETWEEN '" + str(request.args.get('from')) + "' AND '" + str(request.args.get('to')) + "'")
	data = np.array(cur.fetchall())
	data = data.transpose()

	cur.close()

	pwdObject.setMarker('-')
	pwdObject.setData(data[1], data[0], 'Temperatur', 'Datum')

	return pwdObject.createHtmlObject()

@data.route('/temperaturedata')
def tempdata():

	datefrom = datetime.strptime(request.args.get('from'), '%Y-%m-%dT%H:%M:%S.%fZ')
	datefrom = pytz.timezone("UTC").localize(datefrom);
	datefrom = datefrom.astimezone(pytz.timezone("Europe/Berlin"))
	timestringfrom = datefrom.strftime("%Y-%m-%d %H:%M:%S")

	dateto = datetime.strptime(request.args.get('to'), '%Y-%m-%dT%H:%M:%S.%fZ')
	dateto = pytz.timezone("UTC").localize(dateto);
	dateto = dateto.astimezone(pytz.timezone("Europe/Berlin"))
	timestringto = dateto.strftime("%Y-%m-%d %H:%M:%S")

	cur = mysql.connect.cursor()
	cur.execute("SELECT temperature, time FROM Sensordaten WHERE time BETWEEN '" + timestringfrom + "' AND '" + timestringto + "'")
	data = cur.fetchall()
	data = np.array(data)
	data = data.transpose()

	cur.close()

	return jsonify(data=data.tolist());

@data.route('/airhumiditydata')
def airhumiditydata():

	datefrom = datetime.strptime(request.args.get('from'), '%Y-%m-%dT%H:%M:%S.%fZ')
	datefrom = pytz.timezone("UTC").localize(datefrom);
	datefrom = datefrom.astimezone(pytz.timezone("Europe/Berlin"))
	timestringfrom = datefrom.strftime("%Y-%m-%d %H:%M:%S")

	dateto = datetime.strptime(request.args.get('to'), '%Y-%m-%dT%H:%M:%S.%fZ')
	dateto = pytz.timezone("UTC").localize(dateto);
	dateto = dateto.astimezone(pytz.timezone("Europe/Berlin"))
	timestringto = dateto.strftime("%Y-%m-%d %H:%M:%S")

	cur = mysql.connect.cursor()
	cur.execute("SELECT airhumidity, time FROM Sensordaten WHERE time BETWEEN '" + timestringfrom + "' AND '" + timestringto + "'")
	data = cur.fetchall()
	data = np.array(data)
	data = data.transpose()

	cur.close()

	return jsonify(data=data.tolist());

@data.route('/soilhumiditydata')
def soilhumiditydata():

	datefrom = datetime.strptime(request.args.get('from'), '%Y-%m-%dT%H:%M:%S.%fZ')
	datefrom = pytz.timezone("UTC").localize(datefrom);
	datefrom = datefrom.astimezone(pytz.timezone("Europe/Berlin"))
	timestringfrom = datefrom.strftime("%Y-%m-%d %H:%M:%S")

	dateto = datetime.strptime(request.args.get('to'), '%Y-%m-%dT%H:%M:%S.%fZ')
	dateto = pytz.timezone("UTC").localize(dateto);
	dateto = dateto.astimezone(pytz.timezone("Europe/Berlin"))
	timestringto = dateto.strftime("%Y-%m-%d %H:%M:%S")

	cur = mysql.connect.cursor()
	cur.execute("SELECT soilhumidity, time FROM Sensordaten WHERE time BETWEEN '" + timestringfrom + "' AND '" + timestringto + "'")
	data = cur.fetchall()
	data = np.array(data)
	data = data.transpose()

	cur.close()

	return jsonify(data=data.tolist());
