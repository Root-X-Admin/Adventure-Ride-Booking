from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Activity, Booking, db

# Define Blueprint
booking_bp = Blueprint('booking', __name__)
app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def home():
    return render_template('index.html')

@app_routes.route('/activities')
def activity_listing():
    # Get filter parameters
    activity_type = request.args.get('type')
    difficulty = request.args.get('difficulty')
    price_range = request.args.get('price')
    location = request.args.get('location')

    query = Activity.query  # Start query

    # Apply filters
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    if difficulty:
        query = query.filter(Activity.difficulty == difficulty)
    if price_range:
        min_price, max_price = map(int, price_range.split('-'))
        query = query.filter(Activity.price.between(min_price, max_price))
    if location:
        query = query.filter(Activity.location.contains(location))

    activities = query.all()  # Fetch filtered results
    print("Fetched activities:", activities)  # Debugging line

    return render_template('activities.html', activities=activities)

@app_routes.route('/activity/<int:activity_id>')
def activity_detail(activity_id):
    activity = Activity.query.get_or_404(activity_id)  # Fetch activity from database
    return render_template('activity_detail.html', activity=activity)

# Step 1: Select Date & Time
@booking_bp.route('/book/<int:activity_id>', methods=['GET', 'POST'])
def book_activity(activity_id):
    if request.method == 'POST':
        date = request.form['date']
        time_slot = request.form['time_slot']
        return redirect(url_for('booking.participant_details', activity_id=activity_id, date=date, time_slot=time_slot))
    
    return render_template('booking_step1.html', activity_id=activity_id)

# Step 2: Enter Participant Details
@booking_bp.route('/book/participants/<int:activity_id>', methods=['GET', 'POST'])
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

# Step 3: Payment Page
@booking_bp.route('/book/payment/<int:activity_id>', methods=['GET', 'POST'])
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
            activity_id=activity_id, name=name, age=age, contact=contact,
            date=date, time_slot=time_slot, participants=participants, payment_method=payment_method
        )
        db.session.add(new_booking)
        db.session.commit()

        return redirect(url_for('booking.confirmation', booking_id=new_booking.id))

    return render_template('booking_step3.html', activity_id=activity_id, name=name, age=age, contact=contact, participants=participants, date=date, time_slot=time_slot)

# Step 4: Confirmation Page
@booking_bp.route('/book/confirmation/<int:booking_id>')
def confirmation(booking_id):
    booking = Booking.query.get(booking_id)
    return render_template('booking_step4.html', booking=booking)


@app_routes.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        print(f"New Contact Form Submission: {name} ({email}) - {message}")
        flash("Your message has been submitted!", "success")
    return render_template('contact.html')
