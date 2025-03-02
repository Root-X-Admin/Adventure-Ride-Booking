from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Booking, db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def user_dashboard():
    # Fetch all bookings
    bookings = Booking.query.all()

    # Categorize bookings
    upcoming_rides = [b for b in bookings if b.status == "Confirmed"]
    past_activities = [b for b in bookings if b.status == "Completed"]
    total_rewards = sum(b.rewards for b in past_activities)

    return render_template(
        'dashboard.html', 
        upcoming_rides=upcoming_rides, 
        past_activities=past_activities,
        total_rewards=total_rewards
    )

@dashboard_bp.route('/modify/<int:booking_id>', methods=['GET', 'POST'])
def modify_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if request.method == 'POST':
        booking.date = request.form['date']
        booking.time_slot = request.form['time_slot']
        db.session.commit()
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('dashboard.user_dashboard'))

    return render_template('modify_booking.html', booking=booking)

@dashboard_bp.route('/cancel/<int:booking_id>')
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = "Cancelled"
    db.session.commit()
    flash('Booking has been cancelled.', 'warning')
    return redirect(url_for('dashboard.user_dashboard'))

@dashboard_bp.route('/download_invoice/<int:booking_id>')
def download_invoice(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('invoice.html', booking=booking)
