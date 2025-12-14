from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError, NumberRange, DataRequired


#this file is used to create form validation using wtforms which is for Flask apps/
#it provides input validation, adds CSRF tokens, prevents any malformed requests and prevents sql injection
#as it limits the charaters for fields and it enforces a specific type for the fields
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),InputRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(),InputRequired(), Email(), Length(min=2, max=50)])
    nickname = StringField('Nickname', validators=[DataRequired(),InputRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(),InputRequired(), Length(min=8)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),InputRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(),InputRequired(), Length(min=8)])
    submit = SubmitField('Login')

class PlayerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(),InputRequired(), Length(min=2, max=20)])
    team = StringField('Team', validators=[DataRequired(),InputRequired(), Length(min=2, max=20)])
    position = StringField('Position', validators=[DataRequired(),InputRequired(), Length(min=2, max=20)])
    ppg = FloatField('Points Per Game', validators=[DataRequired(),InputRequired()])
    biography = TextAreaField('Biography')
    contract = FloatField('Salary')
    submit = SubmitField('Submit')

class GameForm(FlaskForm):
    date = StringField('Date', validators=[DataRequired(),InputRequired()])
    opponent = StringField('Opponent', validators=[DataRequired(),InputRequired()])
    venue = StringField('Venue', validators=[DataRequired(),InputRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Add game to schedule')