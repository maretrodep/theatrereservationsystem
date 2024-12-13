import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required

from .models import LoyaltyCard, Program, Booking, User, BookedSeat
from . import db
from .roles import role_required
from .email_send import email_send

admin = Blueprint('admin', __name__)


@admin.route('/admin')
@login_required
@role_required('admin')
def dashboard():
    return render_template('admin_dashboard.html')

@admin.route('/admin/add_loyalty_card', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_loyalty_card():
    if request.method == 'POST':
        serial_number = request.form.get('serial_number')

        # Validate the serial number is a number
        if not serial_number.isdigit():
            flash('Serial number must be a valid number.', 'danger')
            return redirect(url_for('admin.add_loyalty_card'))

        # Check if a loyalty card with the same serial number already exists
        existing_card = LoyaltyCard.query.filter_by(serial_number=serial_number).first()
        if existing_card:
            flash('A loyalty card with this serial number already exists.', 'danger')
            return redirect(url_for('admin.add_loyalty_card'))

        # Create a new loyalty card and link it to the user
        loyalty_card = LoyaltyCard(serial_number=serial_number)
        db.session.add(loyalty_card)
        db.session.commit()

        flash('Loyalty card added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin_add_loyalty_card.html')

@admin.route('/admin/add_program', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_program():
    if request.method == 'POST':
        name = request.form.get('name')
        datetime_str = request.form.get('datetime')
        base_price = request.form.get('base_price')
        sale_start_datetime_str = request.form.get('sale_start_datetime')
        description = request.form.get('description')

        # Input validation
        if not name or not datetime_str or not base_price or not sale_start_datetime_str or not description:
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin.add_program'))

        try:
            datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
            sale_start_datetime_obj = datetime.datetime.strptime(sale_start_datetime_str, '%Y-%m-%dT%H:%M')
            base_price = float(base_price)
        except ValueError:
            flash('Invalid date/time or price format.', 'danger')
            return redirect(url_for('admin.add_program'))

        # Add the program
        new_program = Program(
            name=name,
            datetime=datetime_obj,
            base_price=base_price,
            sale_start_datetime=sale_start_datetime_obj,
            description=description,
        )
        db.session.add(new_program)
        db.session.commit()

        flash('Program added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin_add_program.html')

@admin.route('/admin/view_events')
@login_required
@role_required('admin')
def view_events():
    current_time = datetime.datetime.now()

    # Categorize programs
    upcoming_programs = Program.query.filter(Program.datetime >= current_time, Program.is_cancelled == False).order_by(Program.datetime).all()
    cancelled_programs = Program.query.filter_by(is_cancelled=True).order_by(Program.datetime).all()
    past_programs = Program.query.filter(Program.datetime < current_time, Program.is_cancelled == False).order_by(Program.datetime).all()

    return render_template(
        'admin_programs_panel.html',
        upcoming_programs=upcoming_programs,
        cancelled_programs=cancelled_programs,
        past_programs=past_programs,
        current_time=current_time,
    )

@admin.route('/admin/cancel_program', methods=['POST'])
@login_required
@role_required('admin')
def cancel_program():
    program_id = request.args.get('program_id')
    email_subject = request.form.get('email_subject')
    email_body = request.form.get('email_body')
    if not program_id:
        flash('Program ID is missing.', 'danger')
        return redirect(url_for('admin.view_events'))

    # Find the program
    program = Program.query.get(program_id)
    if not program:
        flash('Program not found.', 'danger')
        return redirect(url_for('admin.view_events'))

    # Update the program's status to cancelled
    program.is_cancelled = True
    db.session.commit()

    # Placeholder for sending email
    send_email_function(program_id, email_subject, email_body)

    flash(f'Program "{program.name}" has been cancelled.', 'success')
    return redirect(url_for('admin.view_events'))

def send_email_function(program_id, subject, body):
    # Query all bookings for the given program
    bookings = Booking.query.filter_by(program_id=program_id).all()

    # Retrieve the email addresses of the users who made the bookings
    email_list = [User.query.get(booking.user_id).email for booking in bookings if User.query.get(booking.user_id)]

    if not email_list:
        flash("No bookings found for this program.")
        return

    # Use the email_send function to send emails
    try:
        email_send(email_list, subject, body)
        flash("Emails sent successfully!")
    except Exception as e:
        flash(f"Error while sending emails: {e}")


@admin.route('/admin/send_email', methods=['POST'])
@login_required
@role_required('admin')
def send_email():
    program_id = request.args.get('program_id')
    email_subject = request.form.get('email_subject')
    email_body = request.form.get('email_body')
    if not program_id:
        flash('Program ID is missing.', 'danger')
        return redirect(url_for('admin.view_events'))

    # Placeholder function call
    send_email_function(program_id, email_subject, email_body)

    flash('Email sent successfully!', 'success')
    return redirect(url_for('admin.view_events'))

@admin.route('/admin/view_booked_seats', methods=['GET'])
@login_required
@role_required('admin')
def view_booked_seats():
    program_id = request.args.get('program_id')
    if not program_id:
        flash('Program ID is missing.', 'danger')
        return redirect(url_for('admin.view_events'))

    # Fetch program details
    program = Program.query.get(program_id)
    if not program:
        flash('Program not found.', 'danger')
        return redirect(url_for('admin.view_events'))

    # Fetch booked seats
    booked_seats = BookedSeat.query.join(Booking).filter(Booking.program_id == program_id).all()

    # Format the booked seats into a plain text structure
    booked_seats_list = [f"Row: {seat.row}, Seat: {seat.number}, Category: {seat.category}" for seat in booked_seats]

    return render_template(
        'admin_booked_seats.html',
        program=program,
        booked_seats=booked_seats_list
    )

