from flask import Blueprint, render_template, redirect, url_for
from decorators import login_required
from db import get_db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')  # Redirect root URL to dashboard
@login_required
def home_redirect():
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    c = conn.cursor()

    # Total customers
    c.execute('SELECT COUNT(*) FROM customers')
    total_customers = c.fetchone()[0]

    # Total bills
    c.execute('SELECT COUNT(*) FROM bills')
    total_bills = c.fetchone()[0]

    # Total revenue in last 30 days
    c.execute('''
        SELECT SUM(amount) FROM bills 
        WHERE date >= DATE('now', '-30 days')
    ''')
    total_revenue_30d = c.fetchone()[0] or 0

    # Top 5 customers by total amount spent
    c.execute('''
        SELECT customers.name, SUM(bills.amount) as total_spent
        FROM bills
        JOIN customers ON bills.customer_id = customers.id
        GROUP BY customers.id
        ORDER BY total_spent DESC
        LIMIT 5
    ''')
    top_customers = c.fetchall()

    # Revenue per month (last 6 months)
    c.execute('''
        SELECT strftime('%Y-%m', date) as month, SUM(amount)
        FROM bills
        WHERE date >= DATE('now', '-6 months')
        GROUP BY month
        ORDER BY month ASC
    ''')
    revenue_per_month = c.fetchall()

    # 5 most recent bills
    c.execute('''
        SELECT bills.id, customers.name, bills.service, bills.amount, bills.date
        FROM bills
        LEFT JOIN customers ON bills.customer_id = customers.id
        ORDER BY bills.date DESC
        LIMIT 5
    ''')
    recent_bills = c.fetchall()

    # 5 most recent customers
    c.execute('''
        SELECT id, name, phone, pet_name, date_added
        FROM customers
        ORDER BY date_added DESC
        LIMIT 5
    ''')
    recent_customers = c.fetchall()

    # Total revenue (all time)
    c.execute('SELECT SUM(amount) FROM bills')
    total_revenue_all_time = c.fetchone()[0] or 0

    # Revenue this month (from 1st of current month)
    c.execute('''
        SELECT SUM(amount) FROM bills
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    ''')
    revenue_this_month = c.fetchone()[0] or 0

    # Revenue previous month
    c.execute('''
        SELECT SUM(amount) FROM bills
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now', '-1 month')
    ''')
    revenue_last_month = c.fetchone()[0] or 0

    # Calculate percentage change (avoid division by zero)
    if revenue_last_month > 0:
        revenue_change_pct = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100
    else:
        revenue_change_pct = None  # means "no data last month"

    # Bills added today
    c.execute("SELECT COUNT(*), SUM(amount) FROM bills WHERE DATE(date) = DATE('now')")
    bills_today = c.fetchone()
    bills_today_count = bills_today[0]
    bills_today_amount = bills_today[1] or 0

    # New customers this month
    c.execute("SELECT COUNT(*) FROM customers WHERE strftime('%Y-%m', date_added) = strftime('%Y-%m', 'now')")
    new_customers_this_month = c.fetchone()[0]

    # Returning customers: unique customers with more than one bill
    c.execute('''
        SELECT COUNT(*) FROM (
            SELECT customer_id FROM bills
            GROUP BY customer_id
            HAVING COUNT(*) > 1
        )
    ''')
    returning_customers = c.fetchone()[0]

    # Most popular services by count (last 6 months)
    c.execute('''
    SELECT service, COUNT(*) as count
    FROM bills
    WHERE date >= DATE('now', '-6 months')
    GROUP BY service
    ORDER BY count DESC
    LIMIT 5
    ''')
    popular_services = c.fetchall()  # list of (service, count)

    # Get next 5 upcoming appointments
    c.execute('''
        SELECT a.id, c.name, a.pet_name, a.service, a.date, a.time
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        WHERE date >= DATE('now')
        ORDER BY date, time
        LIMIT 5
    ''')
    upcoming_appointments = c.fetchall()

    conn.close()

    # Prepare data for chart.js
    labels = [row[0] for row in revenue_per_month]
    values = [row[1] or 0 for row in revenue_per_month]

    # Prepare data for top services summary card
    top_services = [{'service': row[0], 'count': row[1]} for row in popular_services]
    return render_template('dashboard.html',
    total_customers=total_customers,
    total_bills=total_bills,
    total_revenue_30d=total_revenue_30d,
    total_revenue_all_time=total_revenue_all_time,
    bills_today_count=bills_today_count,
    bills_today_amount=bills_today_amount,
    new_customers_this_month=new_customers_this_month,
    returning_customers=returning_customers,
    chart_labels=labels,
    chart_values=values,
    recent_bills=recent_bills,
    recent_customers=recent_customers,
    top_customers=top_customers,
    popular_services=popular_services,
    revenue_this_month=revenue_this_month,
    revenue_last_month=revenue_last_month,
    revenue_change_pct=revenue_change_pct,
    upcoming_appointments=upcoming_appointments,
    top_services=top_services
)
