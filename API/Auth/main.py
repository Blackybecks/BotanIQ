from flask import Blueprint, render_template
from flask_login import login_required, current_user
import plots as plt
from db import db
from db import mysql

main = Blueprint('main', __name__)

@main.route('/')
def index():
	return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
	return render_template('profile.html', name=current_user.name)

@main.route('/dashboard')
@login_required
def dashboard():

	print(mysql)
	cur = mysql.connect.cursor()
	cur.execute("SELECT * FROM Sensordaten"); #WHERE time BETWEEN '" + str(request.args.get('from')) + "' AND '" + str(request.args.get('to')) + "'")
	data = cur.fetchall()
	cur.execute("SELECT * FROM Devicestatus"); #WHERE time BETWEEN '" + str(request.args.get('from')) + "' AND '" + str(request.args.get('to')) + "'")
	devices = cur.fetchall()
	cur.close()

	wcd = float(data[-1][3])
	color = 'gray';
	if wcd < 30:
		color = '#ce382e'
	elif wcd < 70:
		color = '#fae333'
	else:
		color = '#74cc44'  

	return render_template('dashboard.html', rows=data, color=color, devices=devices)