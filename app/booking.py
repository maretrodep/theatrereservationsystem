import json
import ast
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Booking, BookedSeat, Program, db

booking = Blueprint('booking', __name__)

@login_required
@booking.route('/booking')
def booking_page():
    program_id = request.args.get('program_id')

    # Validate program ID
    program = Program.query.get_or_404(program_id)

    # Fetch unavailable seats for the program
    unavailable_seats = BookedSeat.query.join(Booking).filter(
        Booking.program_id == program_id
    ).all()
    unavailable_seat_tuples = [
        (seat.row, seat.number, seat.category) for seat in unavailable_seats
    ]

    return render_template(
        'booking.html',
        program=program,
        unavailable_seats=unavailable_seat_tuples
    )

@login_required
@booking.route('/booking_details', methods=['POST'])
def booking_details():
    selected_seats = request.form.get('selected_seats')
    if not selected_seats:
        flash("No seats selected!", category="error")
        return redirect(url_for('booking.booking_page', program_id=request.args.get('program_id')))

    selected_seats = json.loads(selected_seats)

    return render_template(
        'booking_details.html',
        selected_seats=selected_seats,
        program_id=request.args.get('program_id')
    )

@login_required
@booking.route('/finalize_booking', methods=['POST'])
def finalize_booking():
    program_id = request.form.get('program_id')
    selected_seats = request.form.get('selected_seats')
    seat_details = {}

    for key, value in request.form.items():
        if key.startswith('seat_details'):
            parts = key.split('[')
            seat_number = parts[1].rstrip(']')
            field = parts[2].rstrip(']')
            if seat_number not in seat_details:
                seat_details[seat_number] = {}
            seat_details[seat_number][field] = value

    if not program_id or not selected_seats or not seat_details:
        flash("Incomplete booking details!", category="error")
        return redirect(url_for('booking.booking_page', program_id=program_id))

    try:
        # Parse selected_seats manually
        selected_seats = ast.literal_eval(selected_seats)
        if not isinstance(selected_seats, list):
            raise ValueError("Parsed selected_seats is not a list.")
    except (ValueError, SyntaxError) as e:
        flash("Invalid seat selection format!", category="error")
        return redirect(url_for('booking.booking_page', program_id=program_id))
    
    total_price = calculate_total_price(db.session.query(Program).filter_by(id=program_id).first().base_price, selected_seats, list(seat_details.values()), current_user.is_loyalty)
    # Create a new booking
    booking = Booking(user_id=current_user.id, program_id=program_id, price=total_price)  # Update price as needed
    db.session.add(booking)
    db.session.flush()  # Flush to get the booking ID

    # Create booked seats
    seat_detail_list = list(seat_details.values())
    for i, seat in enumerate(selected_seats):
        row, number, category = seat.split('-')
        if i < len(seat_detail_list):
            detail = seat_detail_list[i]
            booked_seat = BookedSeat(
                booking_id=booking.id,
                category=category,
                row=row,
                number=int(number),
                full_name=detail['full_name'],
                age=int(detail['age']),
            )
            db.session.add(booked_seat)
        else:
            flash(f"Missing details for seat {seat}", category="error")
            db.session.rollback()
            return redirect(url_for('booking.booking_page', program_id=program_id))

    db.session.commit()
    flash(f"Booking confirmed with price: {total_price}", category="success")
    return redirect(url_for('main.index'))

def calculate_total_price(base_price, selected_seats, seat_details, is_loyalty):
    # Define concessionary rates as percentages
    under_16_rate = 0.05  # 5% discount for under 16
    over_70_rate = 0.10  # 10% discount for over 70
    loyalty_discount = 0.10  # 10% loyalty discount
    large_party_discount = 0.15  # 15% discount for large parties (if applicable)
    
    # Helper function to calculate seat price multiplier based on uploaded chart
    def get_seat_multiplier(row, category):
        # Mapping seat multipliers based on your pricing chart
        seat_multipliers = {
            'Stalls': {
                'AA': {'Matinee': 2.0, 'Evening': 2.5},
                'A-M': {'Matinee': 1.5, 'Evening': 1.75},
                'P-V': {'Matinee': 1.0, 'Evening': 1.5},
            },
            'Circle': {
                'Row A': {'Matinee': 1.5, 'Evening': 1.75},
            },
            'Upper Circle': {
                'Row A': {'Matinee': 0.8, 'Evening': 1.0},
                'Row B': {'Matinee': 0.75, 'Evening': 1.0},
                # Add other rows and categories here
            },
        }
        # Handle missing values (default multiplier is 1.0)
        return seat_multipliers.get(category, {}).get(row, {}).get('Matinee', 1.0)
    
    total_price = 0
    for i, seat in enumerate(selected_seats):
        row, number, category = seat.split('-')
        multiplier = get_seat_multiplier(row, category)
        seat_price = base_price * multiplier
        
        # Apply the best applicable concession percentage
        age = int(seat_details[i]['age'])
        discounts = []
        if age < 16:
            discounts.append(under_16_rate)
        if age > 70:
            discounts.append(over_70_rate)
        if is_loyalty:
            discounts.append(loyalty_discount)
        
        # Calculate the best discount
        best_discount = max(discounts, default=0)
        seat_price *= (1 - best_discount)
        total_price += seat_price
    
    # Apply large party discount if booking exceeds 10 people
    if len(selected_seats) > 10:
        total_price *= (1 - large_party_discount)
    
    return round(total_price, 2)

