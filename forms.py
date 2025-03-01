from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired

class BookingForm(FlaskForm):
    user_name = StringField("Full Name", validators=[DataRequired()])
    date = DateField("Select Date", format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField("Book Now")
