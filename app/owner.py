from flask import Blueprint, render_template, request
from datetime import datetime
import datetime as dt
from .models import Booking, Program, db, BookedSeat
from flask_login import login_required
from .roles import role_required
from sqlalchemy import func

owner = Blueprint('owner', __name__)

@login_required
@role_required('owner')
@owner.route('/owner_dashboard', methods=['GET', 'POST'])
def dashboard():
    today = datetime.now()

    # Default start and end dates
    start_date = today.replace(day=1)
    end_date = today - dt.timedelta(days=1)

    if request.method == 'POST':
        time_period = request.form.get('time_period')
        if time_period == 'this_month':
            start_date = today.replace(day=1)
            end_date = today - dt.timedelta(days=1)
        elif time_period == 'another_month':
            month = int(request.form.get('month'))
            year = int(request.form.get('year'))
            start_date = datetime(year, month, 1)
            end_date = (start_date + dt.timedelta(days=31)).replace(day=1) - dt.timedelta(days=1)
        elif time_period == 'all_time':
            start_date = datetime.min
            end_date = today

    # Prepare monthly data for the chart
    monthly_data = db.session.query(
        func.extract('year', Program.datetime).label('year'),
        func.extract('month', Program.datetime).label('month'),
        func.count(Program.id).label('program_count'),
        func.sum(Booking.price).label('total_revenue'),
        func.count(BookedSeat.id).label('total_seats')
    ).select_from(Program).join(Booking, Program.id == Booking.program_id).join(BookedSeat, BookedSeat.booking_id == Booking.id).filter(
        Program.datetime >= start_date,
        Program.datetime <= end_date,
        Program.is_cancelled == False
    ).group_by(
        func.extract('year', Program.datetime),
        func.extract('month', Program.datetime)
    ).all()


    # Convert to a JSON-friendly structure
    chart_data = [{
        "year": int(row.year),
        "month": int(row.month),
        "program_count": row.program_count,
        "total_revenue": float(row.total_revenue or 0),
        "total_seats": row.total_seats
    } for row in monthly_data]

    # Total statistics
    programs_run_count = sum(row['program_count'] for row in chart_data)
    booked_seats_count = sum(row['total_seats'] for row in chart_data)
    total_revenue = sum(row['total_revenue'] for row in chart_data)

    return render_template(
        'owner_dashboard.html',
        start_date=start_date,
        end_date=end_date,
        programs_run_count=programs_run_count,
        booked_seats_count=booked_seats_count,
        total_revenue=total_revenue,
        chart_data=chart_data,
        today=today
    )
