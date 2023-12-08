'''
<<<<<<< HEAD
CS3250 - Software Development Methods and Tools - Project 3 Final
Team:SyntaxErrorz
Description: Project 3 User Task Management
=======
CS3250 - Software Development Methods and Tools - Fall 2023
Team: Team Syntax Errorz
Description: Final Project
>>>>>>> dev
'''

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, validators, EmailField, DateField
from wtforms.validators import DataRequired, InputRequired, Length

class SignUpForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SubUserSignUpForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    name = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SignInForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=30)], render_kw={"placeholder": "30 Character Limit"})
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=300)], render_kw={"placeholder": "300 Character Limit"})
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[InputRequired()])
    submit = SubmitField("Create Task")
