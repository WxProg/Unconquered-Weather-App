import os
from flask import Flask, render_template, flash, redirect, url_for, request
from dotenv import load_dotenv
from forms import LoginForm, SignupForm, AddCityForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_fontawesome import FontAwesome
from weather_data import get_weather_data, get_ap_data

load_dotenv(dotenv_path=".env")

# Flask app configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('appSecretKey')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///the_uwa.db'
db = SQLAlchemy(app)

fontawesome = FontAwesome(app)

# --------Configuration for Flask Login-----------
login_manager = LoginManager()
login_manager.init_app(app=app)


@login_manager.user_loader
def load_user(user_id):
    return UwaUser.query.get(int(user_id))


# --------App Users db-----------
class UwaUser(db.Model, UserMixin):
    __tablename__ = 'weather_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


# --------Cities db-----------
class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name_of_city = db.Column(db.String(50), nullable=False)
    state_code = db.Column(db.String(2), nullable=False)
    # Foreign key to Link Users ( each user can have multiple cities but each city belongs to only one user)
    weather_user_id = db.Column(db.Integer, db.ForeignKey("weather_users.id"))


# Creating the db
# with app.app_context():
#     db.create_all()

def add_city(city_name, state_code, user_id):
    new_city = City(
        name_of_city=city_name,
        state_code=state_code,
        weather_user_id=user_id,
    )
    db.session.add(new_city)
    db.session.commit()


@app.route("/")
def home_page():
    return render_template(template_name_or_list='home.html')


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    form = SignupForm()
    if form.validate_on_submit():
        new_user = UwaUser()
        new_user.username = form.username.data
        new_user.email = form.email.data
        confirm_password = form.confirm_password.data
        hash_password = generate_password_hash(password=confirm_password, method='pbkdf2:sha256', salt_length=8)
        new_user.password = hash_password

        existing_user = UwaUser.query.filter((UwaUser.email == new_user.email) |
                                             (UwaUser.username == new_user.username)).first()
        if existing_user is not None:
            if existing_user.email == new_user.email:
                flash(f'The email address {existing_user.email} is already registered. Please try again with a '
                      f'different email address.', category='error')
            else:
                flash(f'The username {existing_user.username} is already taken. Please try again with a different '
                      f'username.', category='error')
            return redirect(url_for(endpoint='signup_page'))
        else:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for(endpoint='login_page'))
    return render_template(template_name_or_list='signup.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = UwaUser.query.filter_by(username=username).first()
        if user:
            if check_password_hash(pwhash=user.password, password=password):
                login_user(user=user)
                return redirect(url_for(endpoint="details_page"))
            else:
                flash(message='Password does not match the username entered. Please try again.', category='error')
        else:
            flash(message=f'This username does not exists. Try again.', category='error')
    return render_template(template_name_or_list='login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for(endpoint='home_page'))


@app.route("/details", methods=["GET", "POST"])
@login_required
def details_page():
    form = AddCityForm()
    weather_user_id = current_user.id
    num_cities = City.query.filter_by(weather_user_id=weather_user_id).count()
    if num_cities >= 5:
        flash(message='You can only add a maximum of 5 cities.', category='error')
        return redirect(url_for(endpoint='details_page'))
    if form.validate_on_submit():
        if form.edit_city.data:
            pass
        elif form.delete_city.data:
            pass
        else:
            add_city(city_name=form.city_name.data,
                     state_code=form.state_code.data,
                     user_id=weather_user_id,)
            return redirect(url_for(endpoint='details_page'))
    cities = City.query.filter_by(weather_user_id=current_user.id).all()
    city_data = []
    for city in cities:
        weather_data = get_weather_data(city_name=city.name_of_city, state_code=city.state_code)
        city_data.append({
            'name': city.name_of_city,
            'state': city.state_code,
            'weather': weather_data,
        })
    return render_template(template_name_or_list='weather_info.html', name=current_user.username, cities=city_data,
                           form=form)
