from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired, ValidationError
from email_validator import validate_email, EmailNotValidError


class EmailValidator:
    def __call__(self, form, field):
        email = field.data
        try:
            # Validate the email using the email_validator package
            valid = validate_email(email)

            # Check if the domain name is a common free email provider
            domain_name = valid.email.split('@')[1]
            common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com']
            if domain_name not in common_domains:
                raise EmailNotValidError("Not a valid email address. Please check your spelling.")

        except EmailNotValidError as e:
            # Raise a validation error with the custom message
            raise ValidationError(str(e))


class SignupForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    email = StringField(label="Email", validators=[InputRequired(), Email(), EmailValidator()])
    password = PasswordField(label="Password", validators=[InputRequired(),
                                                           Length(min=8, max=10)])
    confirm_password = PasswordField(label="Confirm Password", validators=[
        InputRequired(),
        Length(min=8, max=10),
        EqualTo("password", message='Passwords must match!')])
    submit = SubmitField(label="Sign Up")


class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired(),
                                                           Length(min=8, max=10)])
    submit = SubmitField(label="Log In")


class AddCityForm(FlaskForm):
    city_name = StringField(label="City Name:", validators=[DataRequired()])
    state_code = StringField(label="State Code:", validators=[DataRequired(), Length(max=2)])
    add_city = SubmitField(label="Add City")
    edit_city = SubmitField(label="Edit City")
    delete_city = SubmitField(label="Delete City")
