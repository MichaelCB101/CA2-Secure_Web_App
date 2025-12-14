#this is the main app where all the routes to the pages will take place
import limiter
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_login import current_user, login_required, LoginManager, login_user, logout_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from datetime import datetime, timedelta
from config import Config
from model import db, User, Player, Game
from forms import LoginForm, RegisterForm, PlayerForm, GameForm
from security import hash_password, verify_password, sanitize_text, Encryption, isAdmin, sec_headers
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

#initialise the flask web app
app = Flask(__name__)

#create s log file for logging any errors or user actions
LOG_NAME = "logsCA2"
if not os.path.exists(LOG_NAME):
    os.mkdir(LOG_NAME)

log_file = os.path.join(LOG_NAME, "app.log")
#this code will set 500kb before it rotates, and a backup of 20 logs
file_handling = RotatingFileHandler(log_file, maxBytes=500000, backupCount=20)

format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s [%(pathname)s:%(lineno)d]')
file_handling.setFormatter(format)
file_handling.setLevel(logging.INFO)
app.logger.addHandler(file_handling)
app.logger.setLevel(logging.INFO)
app.logger.info("Starting app and log file")


app.config.from_object(Config)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
FERNET_KEY = os.getenv("FERNET_KEY")

db.init_app(app)
migrate = Migrate(app, db)

csrf = CSRFProtect(app)

#create a login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#this code will set a rate limit of logins to the app, used as a security feature to protect the server from too many requests
limit = Limiter(key_func=get_remote_address, app=app, default_limits=["100/day", "10/hour"])

#this code is the fernet encryption, the key is in the env file
fernetKey = os.getenv('FERNET_KEY')
encryption = Encryption(fernetKey)

#this code will implement network and port protection and security. it takes the allowed methods of GET and POST
#and checks against any other non allowed methods like PUT, DELETE, TRACE etc.., and will log it in the log file is there
#is any malicuious attempt with any not allowed methods
@app.before_request
def block_methods():
    allowed_methods = ['GET', 'POST']
    if request.method not in allowed_methods:
        app.logger.warning(f"Unauthorized request {request.method} detected")
        abort(405)

#this code works in a similar way to the above method, where there is a port list of allowed ports to communicate to this web app
#any attempt from other ports will be logged as a warning
@app.before_request
def port_check():
    allowed_ports = ["80", "443", "5000"]
    port = request.environ.get("SERVER_PORT", "UNKNOWN")
    if port not in allowed_ports:
        app.logger.warning(f"Unauthorized request from port:{port} detected")
        abort(403)


#set the security headers from the security file
@app.after_request
def add_header(response):
    return sec_headers(response)

#set the session lifetime
app.permanent_session_lifetime = timedelta(minutes=5)

#this following code sets the routes for the different pages in the web app

#registration page route
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    # if a user witha  username or email exists then it will give the person a message
    if form.validate_on_submit():
        existing = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing:
            flash('Username or email already taken. Please choose a different one.')
            return render_template('register.html', form=form)

        #create a new user nad hash their password with bcrypt, only user accounts can be created, not admins
        hashedPW = hash_password(form.password.data)
        new_user = User(username = form.username.data, email=form.email.data, nickname= form.nickname.data, password_hashed=hashedPW, role="user")
        db.session.add(new_user)
        db.session.commit()

        flash("Thank you for registering. You can now log in.")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#this route is for the login page if there is a successful login then you are redirected to the index page which is the dashboard
@app.route("/login", methods=['GET', 'POST'])
@limiter.limit(5) #limits to 5 log in attempts
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and verify_password(form.password.data, user.password_hashed):
            session.clear()
            login_user(user)
            flash('You have been logged in.')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)


#logout app route clears your session on clicking the logout button
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))


#this is the route to the dashboard page after login, which is the index page in this example
@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


#route for player list from the players created on the add players page, these players info are taken from the db and displayed on the page
@app.route('/players')
@login_required
def player():
    players = Player.query.all()
    return render_template('players.html', players=players)

#route for adding a player to the list inside the database, using post,
@app.route('/players/add_player', methods=['GET', 'POST'])
@login_required
def add_player():
    form = PlayerForm()
    if form.validate_on_submit():
        #this code will clean the text box and sanitise the inputs to prevent malicious attacks
        clean_biography = sanitize_text(form.biography.data)
        player = Player(name = form.name.data, team = form.team.data, position = form.position.data, ppg = form.ppg.data, bio = clean_biography)
        #if the user is an admin they can see the salary field for the player
        if current_user.is_admin:
            salary_str = str(form.contract.data)
            player.secure_salary(salary_str)
            #the player is then added to the database
        db.session.add(player)
        db.session.commit()
        flash('Player has been added successfully')
        return redirect(url_for('add_player'))
    return render_template('add_player.html', form=form)

#make a route to view game schedule, same idea as the players page
@app.route("/schedule")
@login_required
def schedule():
    games = Game.query.all()
    return render_template('schedule.html', games=games)

#add a game to the schedule, which follows the same logic as the add_players page
@app.route("/schedule/add_game", methods=['GET', 'POST'])
@login_required
def add_game():
    form = GameForm()
    if form.validate_on_submit():
        clean_notes = sanitize_text(form.notes.data)
        game = Game(date = form.date.data, opponent = form.opponent.data, venue = form.venue.data, notes = clean_notes)
        db.session.add(game)
        db.session.commit()
        flash('The Game has been added successfully')
        return redirect(url_for('add_game'))
    return render_template('add_game.html', form=form)

#create a route for the admin page, this is only visibile and accessible to admins and they can see encrytpted data here
@app.route("/admin")
@login_required
def admin():
    isAdmin(current_user)
    users = User.query.all()
    players = Player.query.all()
    #this code is added here so the admin as the salary field available to view, but it is encrypted
    salary = {}
    for player in players:
        try:
            salary[player.id] = player.get_salary()
        except:
            salary[player.id] = 0

    return render_template('admin.html', users=users, players=players, salary=salary)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    #app.run(debug=True, host="0.0.0.0", port=5000)
    app.run(debug=True, host="127.0.0.1", port=5000) #use this for running app from python code not in docker container
#change to 0.0.0.0 for docker