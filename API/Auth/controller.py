from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime
from db import db, mysql
import numpy as np

controller = Blueprint('controller', __name__)

@controller.route('/pushdata', methods=['GET'])
def home():

	now = datetime.now()
	timestring = now.strftime("%Y-%m-%d %H:%M:%S")
	connection = mysql.connect
	cur = connection.cursor()
	
	wcd = float(request.args.get('wc'))
	if wcd > 100.0:
		wcd = 100.0
	elif wcd < 0:
		wcd = 0.0



	try:
		t = float(request.args.get('t'))
		sh = float(request.args.get('sh'))
		ah = float(request.args.get('ah'))
		l = float(request.args.get('l'))
		isw = float(request.args.get('isw'))
		rot = float(request.args.get('rot'))
		sl = float(request.args.get('sl'))

		cur.execute("INSERT INTO Sensordaten (cid, temperature, watercontainerdistance, soilhumidity, airhumidity, light, time) VALUES (%s, %s, %s, %s, %s, %s, %s)", (1, t, wcd, sh, ah, l, timestring))
		cur.execute("REPLACE INTO Devicestatus (cid, iswatering, rotation, sunlight) VALUES (%s, %s, %s, %s)", (1, isw, rot, sl))
	
	except ValueError:
		print("some_variable did not contain a number!")

	
	connection.commit()
	cur.close()

	return "OK"