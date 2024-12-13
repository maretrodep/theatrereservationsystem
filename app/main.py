import datetime as dt
from operator import and_
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Program, LoyaltyCard, Booking, BookedSeat
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def index():
    current_time = datetime.now()

    # Get regular programs that are bookable right now and still upcoming
    programs = Program.query.filter(
        Program.sale_start_datetime <= current_time,  # Bookable now
        Program.datetime > current_time,             # Event is in the future
        Program.is_cancelled == False                # Not canceled
    ).order_by(Program.datetime).limit(7).all()

    # Get loyalty programs that are in their booking window and still upcoming
    loyalty_programs = Program.query.filter(
        and_(
            Program.sale_start_datetime > current_time,                    # Starts in the future
            Program.sale_start_datetime <= current_time + dt.timedelta(days=7),  # Within 7-day window
        ),
        Program.datetime > current_time,             # Event is in the future
        Program.is_cancelled == False                # Not canceled
    ).order_by(Program.datetime).limit(3).all()
    return render_template('index.html', programs=programs, loyalty_programs=loyalty_programs)

@main.route('/programs')
def all_programs():
    current_time = datetime.now()

    programs = Program.query.filter(
        Program.sale_start_datetime <= current_time,  # Bookable now
        Program.datetime > current_time,             # Event is in the future
        Program.is_cancelled == False                # Not canceled
    ).order_by(Program.datetime).all()

    # Get loyalty programs that are in their booking window and still upcoming
    loyalty_programs = Program.query.filter(
        and_(
            Program.sale_start_datetime > current_time,                    # Starts in the future
            Program.sale_start_datetime <= current_time + dt.timedelta(days=7),  # Within 7-day window
        ),
        Program.datetime > current_time,             # Event is in the future
        Program.is_cancelled == False                # Not canceled
    ).order_by(Program.datetime).all()

    return render_template('programs.html', programs=programs, loyalty_programs=loyalty_programs)


@login_required
@main.route('/profile')
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/add_loyalty', methods=['GET', 'POST'])
@login_required
def add_loyalty():
    if request.method == 'POST':
        serial_number = request.form.get('serial_number')
        card = LoyaltyCard.query.filter_by(serial_number=serial_number).first()
        if card and not card.user_id:  # Ensure the card exists and is not registered
            loyalty_expire = loyalty_expire = dt.datetime.today() + dt.timedelta(days=31)
            loyalty_expire = loyalty_expire.replace(hour=0, minute=0, second=0, microsecond=0)
            current_user.is_loyalty = True
            current_user.loyalty_expire = loyalty_expire
            card.user_id = current_user.id
            db.session.commit()
            flash('Loyalty card successfully added!', 'success')
        else:
            flash('Invalid or already registered loyalty card.', 'danger')
        return redirect(url_for('main.profile'))

    return render_template('add_loyalty.html')

@login_required
@main.route('/mybookings')
def mybookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    
    # Eagerly load the program for each booking
    for booking in bookings:
        booking.program = Program.query.get(booking.program_id)
        booking.booked_seats = BookedSeat.query.filter_by(booking_id=booking.id).all()

    # Separate bookings into upcoming and past
    upcoming_bookings = []
    past_bookings = []
    
    current_time = datetime.now()

    for booking in bookings:
        if booking.program.datetime > current_time:
            upcoming_bookings.append(booking)
        else:
            past_bookings.append(booking)
    
    return render_template('bookings.html', upcoming_bookings=upcoming_bookings, past_bookings=past_bookings)