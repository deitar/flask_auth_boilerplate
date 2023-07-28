
from flask import Flask, render_template, request, redirect, url_for, flash
import app_config
from flask_login import LoginManager, login_user, login_required, logout_user
from models.user import User, db
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


app = Flask(__name__)

app.config.from_object(app_config)

# initialize the Sqlalchemy db object with flask app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        rememberme = request.form.get('rememberme') and True

        print('rememberme: ', rememberme)

        # Basic validation: Check if both the email and password are provided
        if not email:
            flash('Please provide a email.', 'error')
            return redirect(url_for('login'))

        if not password:
            flash('Please provide a password.', 'error')
            return redirect(url_for('login'))

        # Query the user from the database using the provided email
        user = User.query.filter(func.lower(User.email) == func.lower(email)).first()

        # Validate if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            if login_user(user, remember=rememberme, duration=datetime.timedelta(days=365)):
                return redirect(url_for('profile'))
            else:
                flash('Login attempt failed', 'error')
                
        flash('Invalid email or password', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET','POST'])
def register():

    if request.method=='POST':
        # code to validate and add user to database goes here
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmpassword')

        # validation
        is_valid = True
        if not name:
            flash('Name cannot be blank', 'error')
            is_valid = False
        if not email:
            flash('Email cannot be blank', 'error')
            is_valid = False
        if not password:
            flash('Please enter password', 'error')
            is_valid = False
        if password!=confirm_password:
            flash('Password does not match', 'error')
            is_valid = False

        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('User already exists', 'error')
            # return redirect(url_for('register'))
            is_valid = False

        if is_valid == False:
            return render_template('register.html', name=name, email=email)
        else:
            # create a new user with the form data. Hash the password so the plaintext version isn't saved.
            new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('register_success'))

    return render_template('register.html')


@app.route('/register-success')
def register_success():
    return render_template('register-success.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
    

if __name__ == '__main__':
    # Create the database and tables (Run this once to create the database)
    with app.app_context():
        db.create_all()
    app.run(debug=app.config['DEBUG'])
