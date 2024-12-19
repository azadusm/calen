from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class BookingForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired()])
    submit = SubmitField("Book")
