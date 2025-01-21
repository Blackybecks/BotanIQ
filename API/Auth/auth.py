from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from db import db

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
	return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
	email = request.form.get('email')
	password = request.form.get('password')
	remember = True if request.form.get('remember') else False

	user = User.query.filter_by(email=email).first()

	if not user or not check_password_hash(user.password, password):
		flash('Bitte überprüfen Sie die von Ihnen eingegebenen Daten')
		return redirect(url_for('auth.login'))

	login_user(user, remember=remember)
	flash('Sie haben sich erfolgreich eingeloggt')
	return redirect(url_for('main.dashboard'))

@auth.route('/signup')
def signup():
	return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
	email = request.form.get('email')
	name = request.form.get('name')
	password = request.form.get('password')

	user = User.query.filter_by(email=email).first()

	if user: 
		flash('Die von Ihnen angegebene Email existiert bereits')
		return redirect(url_for('auth.signup'))

	new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

	db.session.add(new_user)
	db.session.commit()

	flash('Sie haben sich erfolgreich registriert')

	return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Sie haben sich erfolgreich ausgeloggt')
	return redirect(url_for('main.index'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash('Bitte loggen Sie sich zuerst ein')
    return redirect(url_for('auth.login'))




	