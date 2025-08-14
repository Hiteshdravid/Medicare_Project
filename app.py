import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message # Import SMTPException for better error handling
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, DateTimeLocalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import traceback

# Initialize the Flask application
app = Flask(__name__)

# --- IMPORTANT SECURITY CONFIGURATION ---
# Use a strong, secret key for form security (CSRF protection)
# On a live server, this should be an environment variable
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-super-secret-key-goes-here-and-is-secure')

# Mail server settings.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dravidchellamuthu@gmail.com'

# SECURITY WARNING: Hardcoding your password is NOT secure for a production app.
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'eghw xhqz eemu rmbn')
app.config['MAIL_DEFAULT_SENDER'] = 'dravidchellamuthu@gmail.com'

# Initialize Flask-Mail with the application
mail = Mail(app)

# Define the new, more detailed form class to match your HTML
class AppointmentForm(FlaskForm):
    fullName = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    doctor = SelectField('Select Doctor', choices=[
        ('', '-- Select a Doctor --'),
        ('dr_smith', 'Dr. Sarah Smith - Cardiology'),
        ('dr_johnson', 'Dr. Michael Johnson - Neurology'),
        ('dr_williams', 'Dr. Emily Williams - Pediatrics'),
        ('dr_brown', 'Dr. James Brown - Orthopedics')
    ], validators=[DataRequired()])
    appointmentDate = DateTimeLocalField('Appointment Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    reason = TextAreaField('Reason for Visit', validators=[Length(max=500)])
    submit = SubmitField('Schedule Appointment')

def send_email(subject, recipient, body):
    """
    Helper function to send an email.
    It returns True on success and False on failure.
    It no longer flashes messages to the user.
    """
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    try:
        mail.send(msg)
        print(f"Email sent to {recipient} successfully.")
        return True

    except Exception as e:
        print(f"Failed to send email to {recipient}. A general error occurred: {e}")
        print("--- Full Traceback ---")
        traceback.print_exc()
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    form = AppointmentForm()
    
    if form.validate_on_submit():
        full_name = form.fullName.data
        email = form.email.data
        doctor_name = dict(form.doctor.choices)[form.doctor.data]
        appointment_date = form.appointmentDate.data
        reason = form.reason.data

        subject = "Appointment Confirmation"
        body = f"""Dear {full_name},

Your appointment with {doctor_name} has been successfully scheduled.

Details:
Appointment Date & Time: {appointment_date.strftime('%A, %B %d, %Y at %I:%M %p')}
Reason for Visit: {reason}

Thank you for choosing our clinic!
"""
        # The main change is here. We check the return value of send_email
        # and flash the message accordingly.
        if send_email(subject, email, body):
            flash('Appointment scheduled successfully! A confirmation email has been sent.', 'success')
        else:
            flash('An error occurred while scheduling your appointment. Please try again.', 'error')
        
        return redirect(url_for('index'))

    return render_template('medicare_scheduler.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
