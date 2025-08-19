from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from functools import wraps
from forms import AppointmentForm 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/Medicare"
mongo = PyMongo(app)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dravidchellamuthu@gmail.com'
app.config['MAIL_PASSWORD'] = 'eghw xhqz eemu rmbn'
app.config['MAIL_DEFAULT_SENDER'] = 'dravidchellamuthu@gmail.com'

mail = Mail(app)

# ---------------------------
# Login Required Decorator
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def index():
    form = AppointmentForm()
    prescriptions = []
    if 'user_id' in session:
        prescriptions = list(mongo.db.prescriptions.find({'user_id': session['user_id']}))
    return render_template('medicare_scheduler.html', form=form,prescriptions=prescriptions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        mongo.db.users.insert_one({'email': email, 'password': password})
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            flash('Login successful!')
            return redirect(url_for('index'))
        flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

# ---------------------------
# Appointment Routes
# ---------------------------
@app.route('/schedule_appointment', methods=['POST'])
@login_required
def schedule_appointment():
    full_name = request.form['full_name']
    email = request.form['email']
    appointment_date = request.form['appointment_date']
    reason = request.form['reason']

    mongo.db.appointments.insert_one({
        'full_name': full_name,
        'email': email,
        'appointment_date': appointment_date,
        'reason': reason,
        'user_id': session['user_id'],
        'status' : 'Scheduled'
    })

    subject = "Appointment Confirmation"
    body = f"Dear {full_name},\n\nYour appointment has been scheduled for {appointment_date}.\nReason: {reason}\n\nThank you!"
    send_email(subject, email, body)

    flash('Appointment scheduled successfully! A confirmation email has been sent.')
    return redirect(url_for('index'))

@app.route('/view_appointments')
@login_required
def view_appointments():
    # Fetch actual scheduled appointments from MongoDB
    appointments = list(mongo.db.appointments.find({
        'user_id': session['user_id'],
        'status': 'Scheduled'
    }))

    # Add predefined sample/demo appointments
   

    # Combine both lists
    all_appointments = appointments 

    return render_template('view_appointments.html', appointments=all_appointments)


@app.route('/cancel_appointment/<appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    appointment = mongo.db.appointments.find_one({'_id': ObjectId(appointment_id)})
    if appointment:
        mongo.db.appointments.update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': {'status': 'Cancelled'}}
        )
        is_sample = request.args.get('sample', 'false').lower() == 'true'
    if is_sample:
    # Remove from sample list instead of DB
        global sample_appointments
        sample_appointments = [a for a in sample_appointments if str(a["_id"]) != appointment_id]

        send_email(
            "Appointment Cancellation",
            appointment['email'],
            f"Your appointment on {appointment['appointment_date']} has been cancelled."
        )
        flash('Appointment cancelled successfully!')
    return redirect(url_for('view_appointments'))


# ---------------------------
# Prescription Routes
# ---------------------------


@app.route('/add_prescription', methods=['POST'])
@login_required
def add_prescription():
    email = request.form['email']
    p_type = request.form['type']
    medication = request.form['medication']
    dosage = request.form['dosage']
    start_date = request.form['start_date']
    end_date = request.form.get('end_date', '')
    instructions = request.form.get('instructions', '')

    mongo.db.prescriptions.insert_one({
        'email': email,
        'type': p_type,
        'medication': medication,
        'dosage': dosage,
        'start_date': start_date,
        'end_date': end_date,
        'instructions': instructions,
        'user_id': session['user_id']
    })

    if 'emailNotification' in request.form:
        subject = "New Prescription Added"
        body = f"Prescription: {medication}\nType: {p_type}\nDosage: {dosage}\nInstructions: {instructions}"
        send_email(subject, email, body)

    flash('Prescription added successfully!')
    return redirect(url_for('index'))

@app.route('/delete_prescription/<prescription_id>')
@login_required
def delete_prescription(prescription_id):
    prescription = mongo.db.prescriptions.find_one({'_id': ObjectId(prescription_id)})
    if prescription:
        mongo.db.prescriptions.delete_one({'_id': ObjectId(prescription_id)})
        flash('Prescription deleted successfully!')
    return redirect(url_for('index'))


# ---------------------------
# Email Function
# ---------------------------
def send_email(subject, recipient, body):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)
