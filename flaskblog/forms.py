from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.ext.django.fields import ModelSelectField


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class ItemForm(FlaskForm):
    Product_ID = IntegerField('Product ID (Int)', validators=[DataRequired()])
    price = FloatField('Price (Decimal)', validators=[DataRequired()])
    product_name = TextAreaField('Product name (Text)', validators=[DataRequired()])
    quantity = IntegerField('Quantity (Int)', validators=[DataRequired()])
    #####
    Individual_ID = IntegerField('Individual ID (Int)', validators=[DataRequired()])
    expiration_date = TextAreaField('Expiration Date (Text)', validators=[DataRequired()])
    product_weight = FloatField('Product Weight (Decimal)', validators=[DataRequired()])
    #####
    submit = SubmitField('Add')

class SearchForm(FlaskForm):
    category = TextAreaField('Category (Text)', validators=[DataRequired()])
    searchCritereaNumber = FloatField('Search For (Number): ', validators=[DataRequired()])
    searchCritereaText = TextAreaField('Search For (Text (put in something for testing)): ', validators=[DataRequired()])
    submit = SubmitField('Search')
