from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from __init__ import db, bcrypt, mail
from models import Activity, Booking, User, TempUser
from flask import make_response, current_app
from flask_mail import Message
import random
import string
import re


# Define Blueprints
booking_bp = Blueprint('booking', __name__)
app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
@app_routes.route('/index')
@app_routes.route('/home')
def home():
    activities = Activity.query.all()
     # Fetch the top 3 activities based on rating in descending order
    top_rated_activities = Activity.query.order_by(Activity.rating.desc()).limit(3).all()

    # Ensure ratings are float
    for activity in top_rated_activities:
        activity.rating = float(activity.rating)

    return render_template('index.html', activities=top_rated_activities)

@app_routes.route('/activities')
def activity_listing():
    activity_type = request.args.get('type')
    difficulty = request.args.get('difficulty')
    price_range = request.args.get('price')
    location = request.args.get('location')

    query = Activity.query
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    if difficulty:
        query = query.filter(Activity.difficulty == difficulty)
    if price_range:
        min_price, max_price = map(int, price_range.split('-'))
        query = query.filter(Activity.price.between(min_price, max_price))
    if location:
        query = query.filter(Activity.location.contains(location))

    activities = query.all()
    return render_template('activities.html', activities=activities)

@app_routes.route('/activity/<int:activity_id>')
def activity_detail(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    return render_template('activity_detail.html', activity=activity)

@booking_bp.route('/book/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def book_activity(activity_id):
    if request.method == 'POST':
        date = request.form['date']
        time_slot = request.form['time_slot']
        return redirect(url_for('booking.participant_details', activity_id=activity_id, date=date, time_slot=time_slot))

    return render_template('booking_step1.html', activity_id=activity_id)

@booking_bp.route('/book/participants/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def participant_details(activity_id):
    date = request.args.get('date')
    time_slot = request.args.get('time_slot')

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        contact = request.form['contact']
        participants = request.form['participants']
        
        return redirect(url_for('booking.payment', activity_id=activity_id, name=name, age=age, contact=contact, participants=participants, date=date, time_slot=time_slot))

    return render_template('booking_step2.html', activity_id=activity_id, date=date, time_slot=time_slot)

@booking_bp.route('/book/payment/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def payment(activity_id):
    name = request.args.get('name')
    age = request.args.get('age')
    contact = request.args.get('contact')
    participants = request.args.get('participants')
    date = request.args.get('date')
    time_slot = request.args.get('time_slot')

    if request.method == 'POST':
        payment_method = request.form['payment_method']
        
        new_booking = Booking(
            activity_id=activity_id, user_id=current_user.id, name=name, age=age, contact=contact,
            date=date, time_slot=time_slot, participants=participants, payment_method=payment_method
        )
        db.session.add(new_booking)
        db.session.commit()

        # ✅ Send Confirmation Email
        send_confirmation_email(new_booking)

        return redirect(url_for('booking.confirmation', booking_id=new_booking.id))

    return render_template('booking_step3.html', activity_id=activity_id, name=name, age=age, contact=contact, participants=participants, date=date, time_slot=time_slot)

def send_confirmation_email(booking):
    """Sends a booking confirmation email to the user."""
    user = User.query.get(booking.user_id)  # Fetch user details

    if not user:
        print("❌ Error: User not found!")
        return

    subject = "🎉 Booking Confirmation - Adventure Ride"
    recipient_email = user.email
    body = f"""
    Hello {user.username},

    Your adventure ride has been successfully booked! 🚀

    🏔 **Booking Details:**
    ----------------------------
    📌 Booking ID: {booking.id}
    🎢 Activity: {booking.activity.name if booking.activity else 'Unknown'}
    👤 Name: {booking.name}
    📞 Contact: {booking.contact}
    👥 Participants: {booking.participants}
    📅 Date: {booking.date}
    ⏰ Time Slot: {booking.time_slot}
    💳 Payment Method: {booking.payment_method}
    ✅ Status: {booking.status}
    ----------------------------
    
    We look forward to seeing you on your adventure! 🌟

    Regards,  
    **Adventure Ride Team**
    """

    msg = Message(subject, recipients=[recipient_email], body=body, sender=user.email)

    try:
        with current_app.app_context():  # Ensure mail is sent within app context
            mail.send(msg)
        print("✅ Confirmation email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")


@booking_bp.route('/book/confirmation/<int:booking_id>')
@login_required
def confirmation(booking_id):
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()
    return render_template('booking_step4.html', booking=booking)

@app_routes.route('/dashboard')
@login_required
def user_dashboard():
    today = datetime.now().date()

    # Fetch only the logged-in user's bookings
    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    upcoming_rides = []
    past_activities = []

    for booking in bookings:
        try:
            booking_date = datetime.strptime(booking.date, "%Y-%m-%d").date()
        except ValueError:
            continue  # Skip invalid dates

        # Fetch activity details
        activity = Activity.query.get(booking.activity_id)
        activity_name = activity.name if activity else "Unknown Activity"

        booking_info = {
            'id': booking.id,
            'activity_name': activity_name,
            'date': booking_date,
            'time_slot': booking.time_slot
        }

        if booking_date >= today and booking.status == "Confirmed":
            upcoming_rides.append(booking_info)
        elif booking_date < today and booking.status == "Completed" or booking.status == "Confirmed":
            past_activities.append(booking_info)

    total_rewards = sum(b.rewards for b in bookings if b.status == "Completed")

    return render_template(
        'dashboard.html',
        upcoming_rides=upcoming_rides,
        past_activities=past_activities,
        total_rewards=total_rewards
    )

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))  # 6-digit OTP

# Function to validate username
def is_valid_username(username):
    return bool(re.fullmatch(r"[A-Za-z]{2,50}", username))

# Function to validate password
def is_valid_password(password):
    return bool(re.fullmatch(r"[A-Za-z0-9]{6,}", password))

@app_routes.route('/register', methods=['GET', 'POST'])
def register():
    errors = {}
    username = ''
    email = ''
    
    if request.method == 'POST':
        # Clear session only when starting fresh registration
        if 'otp_verified' in session:
            session.pop('otp_verified', None)

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            errors['email'] = "Email already registered. Please log in."
            return render_template('register.html', errors=errors, username=username, email=email)

        # Validate username
        if not username:
            errors['username'] = "Username is required."
        elif len(username) < 2:
            errors['username'] = "Username must be at least 2 characters long."
        elif len(username) > 50:
            errors['username'] = "Username cannot exceed 50 characters."
        # elif not username.isalpha():
        #     errors['username'] = "Username can only contain letters (A-Z, a-z)."

        # Validate password
        if not password:
            errors['password'] = "Password is required."
        elif len(password) < 6:
            errors['password'] = "Password must be at least 6 characters long."
        elif not re.fullmatch(r"[A-Za-z0-9]+", password):
            errors['password'] = "Password can only contain letters and numbers."

        # If there are errors, re-render the form with error messages
        if errors:
            return render_template('register.html', errors=errors, username=username, email=email)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Generate OTP and expiration time
        otp = generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=5)  # OTP expires in 5 minutes

        # Store user temporarily until OTP is verified
        temp_user = TempUser.query.filter_by(email=email).first()
        if temp_user:
            # Update OTP if user exists in temp storage
            temp_user.username = username
            temp_user.otp = otp
            temp_user.otp_expiry = otp_expiry
            temp_user.password_hash = hashed_password
        else:
            temp_user = TempUser(username=username, email=email, password_hash=hashed_password, otp=otp, otp_expiry=otp_expiry)
            db.session.add(temp_user)

        db.session.commit()

        session['email'] = email # Store email in session for verification

        # Send OTP email
        msg = Message(
                    subject="Verify Your Account for Adventure Ride Booking- OTP Inside",
                    sender="your_email@example.com",
                    recipients=[email]
                )
        msg.body = (
                    f"Hi {username},\n\n"
                    f"Your OTP for verification is: {otp} \n\n"
                    "Please enter this code within 5 minutes to complete your registration.\n\n"
                    "Best regards,\n"
                    "Adventure Ride"
                )
        mail.send(msg)

        flash('OTP sent to your email. Please verify to complete registration.', 'info')
        return redirect(url_for('app_routes.verify_otp'))

    return render_template('register.html', errors=errors, username=username, email=email)

@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    errors = {}
    email = ''
    otp_verified = session.pop('otp_verified', False)  # Remove flag after checking

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user:
            errors['email'] = "No account found with this email."
        elif not bcrypt.check_password_hash(user.password_hash, password):
            errors['password'] = "Incorrect password."
        else:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('app_routes.home'))

        # If errors exist, re-render the login form with messages
        return render_template('login.html', errors=errors, email=email, otp_verified=otp_verified)

    return render_template('login.html', errors=errors, email=email, otp_verified=otp_verified)

@app_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('app_routes.home'))

@booking_bp.route('/modify_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def modify_booking(booking_id):
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        new_date = request.form['date']
        new_time_slot = request.form['time_slot']

        # Update booking details
        booking.date = new_date
        booking.time_slot = new_time_slot
        db.session.commit()
        
        flash("Your booking has been updated!", "success")
        return redirect(url_for('app_routes.user_dashboard'))

    return render_template('modify_booking.html', booking=booking)

@booking_bp.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()

    if booking.status == "Cancelled":
        flash("This booking is already cancelled.", "warning")
        return redirect(url_for('app_routes.user_dashboard'))

    booking.status = "Cancelled"
    db.session.commit()
    
    flash("Your booking has been cancelled successfully.", "success")
    return redirect(url_for('app_routes.user_dashboard'))

@app_routes.route('/download_invoice/<int:booking_id>')
@login_required
def download_invoice(booking_id):
    # Fetch the booking details, including activity relationship
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()

    # Fetch user details
    user = User.query.get(booking.user_id)

    # Fetch activity details using the relationship
    activity = Activity.query.get(booking.activity_id)  # Ensure the activity is retrieved

    invoice_content = f"""
    Booking Invoice
    ---------------------------
    Booking ID: {booking.id}
    Activity Name: {activity.name if Activity else 'Unknown'}
    Username: {user.username if User else 'Unknown'}
    Email: {user.email if User else 'Unknown'}
    Full Name: {booking.name}
    Date: {booking.date}
    Time Slot: {booking.time_slot}
    Participants: {booking.participants}
    Payment Method: {booking.payment_method}
    Status: {booking.status}
    ---------------------------
    Thank you for booking with us!
    """

    response = make_response(invoice_content)
    response.headers["Content-Disposition"] = f"attachment; filename=invoice_{booking.id}.txt"
    response.headers["Content-Type"] = "text/plain"
    return response

@app_routes.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        user_email = current_user.email  # Get the email of the logged-in user
        user_name = request.form['name']
        user_message = request.form['message']

        # Create a new email message
        msg = Message('New Contact Form Submission',  # Subject
                      sender=current_user.email,  # Logged-in user's email as sender
                      recipients=[current_app.config['MAIL_USERNAME']],  # Fixed recipient email
                      reply_to=user_email
                    )
        msg.body = f"""
        Name: {user_name}
        Email: {user_email}
        Message: {user_message}
        """
        # print(user_email)
        try:
            mail.send(msg)  # Send the email
            flash("Your message has been sent successfully!", "success")
            return redirect(url_for('app_routes.home'))  # Redirect to a success page (optional)
        except Exception as e:
            flash(f"Error sending message: {str(e)}", "danger")
            # return f"Error: {str(e)}"  # Return an error message if sending fails
            return redirect(url_for('app_routes.contact'))
    return render_template('contact.html')

@app_routes.route('/success')
def success():
    return render_template('index.html')  # Create a success.html page for confirmation


@app_routes.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'email' not in session:
        flash("Session expired. Please register again.", "danger")
        return redirect(url_for('app_routes.register'))

    email = session['email']
    temp_user = TempUser.query.filter_by(email=email).first()

    if not temp_user:
        flash("Invalid request. Please register again.", "danger")
        return redirect(url_for('app_routes.register'))

    if request.method == 'POST':
        entered_otp = request.form['otp']

        if temp_user.otp == entered_otp and temp_user.otp_expiry > datetime.utcnow():
            # ✅ OTP is correct and not expired → Move user to permanent storage            
            new_user = User(username=temp_user.username, email=temp_user.email, password_hash=temp_user.password_hash)
            db.session.add(new_user)
            db.session.delete(temp_user)  # Remove temporary user record
            db.session.commit()

            # ✅ Set session variable only AFTER successful verification
            session['otp_verified'] = True  # ✅ Store session flag

            flash("OTP verified! Please log in.", "success")
            return redirect(url_for('app_routes.login', otp_verified=1))
        else:
            flash("Invalid or expired OTP. Please try again.", "danger")
            return redirect(url_for('app_routes.verify_otp', otp_invalid=1))

    return render_template('verify_otp.html')