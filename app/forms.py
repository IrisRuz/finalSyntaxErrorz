from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, validators, EmailField, DateField
from wtforms.validators import DataRequired, InputRequired

class SignUpForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SignInForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[InputRequired()])
    submit = SubmitField("Create Task")