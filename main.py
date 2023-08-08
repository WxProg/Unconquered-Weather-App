import os
from datetime import date
from bson.objectid import ObjectId
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message, Mail
from flask import Flask, render_template, flash, redirect, url_for
from dotenv import load_dotenv
from forms import LoginForm, SignupForm, AddCityForm, ChooseBackgroundForm, ForgetPasswordFormForgetUsernameForm, \
    ResetPasswordForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from weather_data import get_weather_data
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap5

load_dotenv(dotenv_path=".env")

# Flask App Configurations
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv('appSecretKey')
app.config["MONGO_URI"] = f"mongodb+srv://chadmysta18:{os.getenv('mongodb_password')}@cluster0.mzcfimv.mongodb.net" \
                          f"/weatherApp?retryWrites=true&w=majority"
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('appSecretPassword')

# Flask-Mail Config / Sending Emails
app.config['MAIL_SERVER'] = os.getenv('mailServer')
app.config['MAIL_PORT'] = os.getenv('mailPort')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('defaultSender')
app.config['MAIL_USERNAME'] = os.getenv('mailUsername')
app.config['MAIL_PASSWORD'] = os.getenv('flaskMailPassword')
app.config['MAIL_USE_SSL'] = True
mail = Mail(app=app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'static', 'images')

# ------- MongoDB -------------
mongo = PyMongo(app)
db = mongo.db
usersCollection = db['Users']
# Username field in mongodb will be unique
usersCollection.create_index("username", unique=True)

# ------- Bootstrap -------------
bootstrap = Bootstrap5(app=app)

# -------- Configuration for Flask Login -----------
login_manager = LoginManager()
login_manager.init_app(app=app)

# ----------- Flask-Login initialization -----------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'


@login_manager.user_loader
def load_user(user_id):
    return User.get(ObjectId(user_id))


# -------- User Model for Flask-Login. Complements the loader function above -----------
class User(UserMixin):
    def __init__(self, username, _id):
        self.username = username
        self._id = str(_id)

    def get_id(self):  # Override get_id
        return self._id

    @staticmethod
    def get(_id):
        user_data = usersCollection.find_one({"_id": _id})
        if not user_data:
            return None
        return User(username=user_data['username'], _id=user_data['_id'])


@app.route("/")
def home_page():
    current_year = date.today().year
    return render_template(template_name_or_list='home.html', current_year=current_year)


@app.route("/forget_username", methods=["GET", "POST"])
def forget_username():
    form = ForgetPasswordFormForgetUsernameForm()

    if form.validate_on_submit():
        email = form.email.data
        user = usersCollection.find_one({"email": email})

        if user:
            try:
                html = render_template(template_name_or_list='usernameRetrieve.html', user=user)
                msg = Message(subject='Retrieve Username',
                              sender=app.config['MAIL_DEFAULT_SENDER'],
                              recipients=[email],
                              html=html)
                mail.send(message=msg)

                flash(message='If the email you entered is registered, you will receive an email with your username.',
                      category='success')
            except Exception as e:
                flash(message=f'Error sending email: {e}', category='danger')
        else:
            flash(message='No user found with that email address.', category='danger')

        return redirect(url_for(endpoint='login_page'))

    return render_template(template_name_or_list='forgetUsername.html', form=form)


@app.route("/forget_password", methods=["GET", "POST"])
def forget_password():
    form = ForgetPasswordFormForgetUsernameForm()

    if form.validate_on_submit():
        email = form.email.data
        user = usersCollection.find_one({"email": email})

        if user:
            # generate a secret token
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = serializer.dumps(str(user['_id']), salt=app.config['SECURITY_PASSWORD_SALT'])

            # send email with reset instructions
            reset_url = url_for(endpoint='reset_password', token=token, _external=True)
            html = render_template(template_name_or_list='emailResetPassword.html', reset_url=reset_url, user=user)
            msg = Message(subject='Reset your password', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email],
                          html=html)
            try:
                mail.send(msg)
                flash(message='If the email you entered is registered, you will receive an email to reset your '
                              'password.',
                      category='success')
            except Exception as e:
                print(e)  # or log the exception
                flash(message='Unable to send the email. Please try again later.', category='danger')

        else:
            flash(message='If the email you entered is registered, you will receive an email to reset your password.',
                  category='success')

        return redirect(url_for(endpoint='login_page'))

    return render_template(template_name_or_list='forgetPassword.html', form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()

    if form.validate_on_submit():
        password = form.password.data

        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            user_id = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
        except(SignatureExpired, BadSignature):
            flash(message='The reset link is invalid or has expired.', category='danger')
            return redirect(url_for(endpoint='login_page'))
        user = usersCollection.find_one({"_id": ObjectId(user_id)})
        if not user:
            flash(message='No user found with that token.', category='danger')
            return redirect(url_for(endpoint='login_page'))

        new_password = generate_password_hash(password=password, method='pbkdf2:sha256', salt_length=8)
        result = usersCollection.update_one({"_id": ObjectId(user_id)}, {"$set": {"password": new_password}})

        if result.modified_count > 0:
            flash(message='Your password has been updated!', category='success')
            return redirect(url_for('login_page'))
        else:
            flash(message='Unable to update your password. Please try again.', category='error')

    return render_template(template_name_or_list='resetPassword.html', form=form, token=token)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for(endpoint='home_page'))


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    form = SignupForm()

    if form.validate_on_submit():
        confirm_password = form.password.data
        hash_password = generate_password_hash(password=confirm_password, method='pbkdf2:sha256', salt_length=8)
        new_user = {
            "username": form.username.data,
            "email": form.email.data,
            "password": hash_password
        }

        existing_user = usersCollection.find_one(
            {"$or": [{'username': form.username.data}, {'email': form.email.data}]})

        if existing_user:
            if existing_user["email"] == new_user["email"]:
                flash(message=f'The email address {existing_user["email"]} already exists.', category='danger')
                return redirect(url_for(endpoint='signup_page'))
            elif existing_user["username"] == new_user["username"]:
                flash(message=f'The username {existing_user["username"]} is already taken.', category='danger')
                return redirect(url_for(endpoint='signup_page'))
        else:
            flash(message='User registered successfully!', category='success')
            usersCollection.insert_one(new_user)
            return redirect(url_for(endpoint='login_page'))
    return render_template(template_name_or_list='signup.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    current_year = date.today().year
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = usersCollection.find_one({'username': username})
        if user:
            password_correct = check_password_hash(pwhash=user["password"], password=password)
            if password_correct:
                login_user(user=User(username=user["username"], _id=user['_id']))
                return redirect(url_for(endpoint='details_page'))
            else:
                flash(message='Invalid password.', category='danger')
        else:
            flash(message='Username does not exists. Check your spelling or signup!', category='danger')
    return render_template(template_name_or_list='login.html', form=form, current_year=current_year)


@app.route("/details", methods=["GET", "POST"])
@login_required
def details_page():
    add_city_form = AddCityForm()

    user_document = usersCollection.find_one({"username": current_user.username})

    # Initialize 'cityDetails' as an empty list if it doesn't exist
    city_details = user_document.get('cityDetails', [])

    # --------------- Customer Background Settings --------------------------------------------
    # choose_background_form = ChooseBackgroundForm()

    # choose_background_form.background.choices = [(img, img) for img in os.listdir(IMG_DIR)
    #                                              if (img.endswith('.jpg') or img.endswith('.png'))
    #                                              and img.startswith('user')]
    #
    # if 'background_image' not in session:
    #     session['background_image'] = choose_background_form.background.choices[0][0]  # default to the first image
    #
    # if choose_background_form.validate_on_submit():
    #     session['background_image'] = choose_background_form.background.data
    #     return redirect(url_for('details_page'))

    # The below code must be added to render_template function
    # --- background_image = session['background_image']
    # --- choose_background_form = choose_background_form

    # ------------------------------------------------------------------------------------------

    if add_city_form.validate_on_submit():
        if len(city_details) >= 6:
            flash(message='You have already added the maximum number of cities. Please remove a city before adding a '
                          'new one.', category='danger')
            return redirect(url_for('details_page'))
        new_city = {
            "cityName": add_city_form.city_name.data.title(),
            "stateCode": add_city_form.state_code.data.upper(),
            "weatherData": get_weather_data(city_name=add_city_form.city_name.data,
                                            state_code=add_city_form.state_code.data),
        }

        city_exists = any(
            city['cityName'] == new_city['cityName']
            and city['stateCode'] == new_city['stateCode']
            for city in city_details
        )

        if city_exists:
            flash(message='You have already added this city,', category='danger')
        else:
            usersCollection.update_one(
                {"username": current_user.username},
                {"$push": {"cityDetails": new_city}}
            )
            flash(message='City added successfully!', category='success')
            return redirect(url_for('details_page'))

        # background_image = session['background_image']
        # choose_background_form = choose_background_form

    return render_template(template_name_or_list='weather_info.html', form=add_city_form, city_details=city_details,
                           whoami=current_user.username)


@app.route("/delete", methods=["POST"])
def city_delete():
    form = AddCityForm()

    city_name = form.city_name.data
    state_code = form.state_code.data

    user_document = usersCollection.find_one({"username": current_user.username})

    city_details = user_document.get('cityDetails', [])

    city_exists = any(
        city['cityName'] == city_name
        and city['stateCode'] == state_code
        for city in city_details
    )

    if city_exists:
        usersCollection.update_one(
            {"username": current_user.username},
            {"$pull": {"cityDetails": {"cityName": city_name, "stateCode": state_code}}}
        )
        flash(message='City deleted successfully.', category='success')
    else:
        flash(message='You cannot delete a city that is not attached to your account.', category='danger')

    return redirect(url_for(endpoint='details_page'))
