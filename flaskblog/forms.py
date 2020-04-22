import validator as validator
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, FloatField, \
    SelectField, TextField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, optional
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
    searchCritereaText = TextAreaField('Search For (Text (Optional)): ', validators=[optional()])
    submit = SubmitField('Search')


class UpdateItem(FlaskForm):
    Product_ID = IntegerField('Product ID (Required)', validators=[DataRequired()])
    expirationDate = StringField('Item Expiration Date (Required)', validators=[DataRequired()])
    amountToAdd = IntegerField('Amount to Add (Optional)', validators=[DataRequired()])
    submit = SubmitField('Submit')


class DeleteItem(FlaskForm):
    Product_ID = IntegerField('Product ID (Required)', validators=[optional()])
    Individual_ID = IntegerField('Individual_ID (Required)', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AdvancedSearchFrontForm(FlaskForm):
    options = [('Get Max', 'Get Max'),
               ('Search Expiration', 'Search Expiration'),
               ('Simulate Transaction', 'Simulate Transaction')]
    SearchOption = SelectField('Search Criterea', choices=options)
    submit = SubmitField('Submit')

class SearchMaxForm(FlaskForm):
    catagory = [('Price', 'Price'),
                ('Product ID', 'Product ID'),
                ('Weight', 'Weight'),]
    SearchOption = SelectField('Catagory', choices=catagory)
    submit = SubmitField('Submit for Max')

class SearchExpirationForm(FlaskForm):
    action = [('Show All', 'Show All'),
              ('Search By Range', 'Search By Range'),
              ('Search For Date', 'Search For Date')]

    SearchOption = SelectField('Type of Search', choices=action)
    SearchTextOne = StringField('Month (Lower Bound or Single Choice)', validators=[optional()])
    SearchIntOne = IntegerField('Year (Lower Bound or Single Choice)', validators=[optional()])
    SearchTextTwo = StringField('Month', validators=[optional()])
    SearchIntTwo = IntegerField('Year', validators=[optional()])

    submit = SubmitField('Submit for Search')

class DisplayItemsForm(FlaskForm):
    submit = SubmitField('Display All Items')


class SimulatedTransactionForm(FlaskForm):
    transaction = TextAreaField('Products In Transaction', validators=[DataRequired()])
    submit = SubmitField('Process Transaction')
