from flask import Blueprint, render_template, redirect, url_for
from decorators import login_required
from db import get_db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/') # Redirect root URL to dashboard
@login_required
def home_redirect():
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    c = conn.cursor()

    # Existing queries
    c.execute('SELECT COUNT(*) FROM customers')
    total_customers = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM bills')
    total_bills = c.fetchone()[0]

    c.execute('''
        SELECT SUM(amount) FROM bills 
        WHERE date >= DATE('now', '-30 days')
    ''')
    total_revenue_30d = c.fetchone()[0] or 0

    # NEW: get revenue per month (last 6 months)
    c.execute('''
        SELECT strftime('%Y-%m', date) as month, SUM(amount)
        FROM bills
        WHERE date >= DATE('now', '-6 months')
        GROUP BY month
        ORDER BY month ASC
    ''')
    revenue_per_month = c.fetchall()  # list of (month, sum)

    conn.close()

    # separate into labels and data for chart.js
    labels = [row[0] for row in revenue_per_month]
    values = [row[1] or 0 for row in revenue_per_month]

    return render_template('dashboard.html',
        total_customers=total_customers,
        total_bills=total_bills,
        total_revenue_30d=total_revenue_30d,
        chart_labels=labels,
        chart_values=values
    )
