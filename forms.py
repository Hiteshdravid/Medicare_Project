from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields import DateTimeLocalField


class AppointmentForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    appointment_date = DateTimeLocalField('Appointment Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    reason = TextAreaField('Reason for Visit')
    doctor = SelectField(
        'Select Doctor',
        choices=[
            ('dr_smith', 'Dr. Sarah Smith - Cardiology'),
            ('dr_johnson', 'Dr. Michael Johnson - Neurology'),
            ('dr_williams', 'Dr. Emily Williams - Pediatrics'),
            ('dr_brown', 'Dr. James Brown - Orthopedics')
        ]
    )
    submit = SubmitField('Schedule Appointment')
