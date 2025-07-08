from decorators import login_required
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response,abort
from db import get_db
from datetime import datetime
from weasyprint import HTML


bills_bp = Blueprint('bills', __name__)

# bills.py

@bills_bp.route('/bills')
@login_required
def bills():
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    conn = get_db()
    c = conn.cursor()

    # Get filter params from request
    customer = request.args.get('customer', '').strip()
    service = request.args.get('service', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    # Build query dynamically
    query = '''
        SELECT bills.id, customers.name, bills.service, bills.amount, bills.date, bills.notes
        FROM bills
        LEFT JOIN customers ON bills.customer_id = customers.id
        WHERE 1=1
    '''
    count_query = '''
        SELECT COUNT(*)
        FROM bills
        LEFT JOIN customers ON bills.customer_id = customers.id
        WHERE 1=1
    '''
    params = []
    count_params = []

    if customer:
        query += ' AND customers.name LIKE ?'
        count_query += ' AND customers.name LIKE ?'
        params.append(f'%{customer}%')
    if service:
        query += ' AND bills.service LIKE ?'
        count_query += ' AND bills.service LIKE ?'
        params.append(f'%{service}%')
    if start_date:
        query += ' AND bills.date >= ?'
        count_query += ' AND bills.date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND bills.date <= ?'
        count_query += ' AND bills.date <= ?'
        params.append(end_date)

    query += ' ORDER BY bills.date DESC LIMIT ? OFFSET ?'
    count_query += ' ORDER BY bills.date DESC'
    params += [per_page, offset]

    c.execute(count_query, params[:-2])
    total_bills = c.fetchone()[0]

    c.execute(query, params)
    bills = c.fetchall()
    conn.close()

    total_pages = (total_bills + per_page - 1) // per_page
    return render_template('bills.html', bills=bills, page=page, total_pages=total_pages, customer=customer, service=service, start_date=start_date, end_date=end_date)


@bills_bp.route('/add_bill', methods=['GET', 'POST'])
@login_required
def add_bill():
    if session.get('role') != 'admin':
        flash('Only admins can add bills.', 'danger')
        return redirect(url_for('bills.bills'))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, phone, email, pet_name, pet_type, notes FROM customers")
    customers = c.fetchall()
    customer_details = {}
    for cust in customers:
        customer_details[cust[0]] = {
            'name': cust[1],
            'phone': cust[2],
            'email': cust[3],
            'pet_name': cust[4],
            'pet_type': cust[5],
            'notes': cust[6]
        }
    # Always fetch all appointments with all needed fields for JS
    c.execute('''
        SELECT a.id, a.date, a.service, a.notes, p.pet_name, p.pet_type, p.size, a.time, a.duration, a.customer_id
        FROM appointments a
        JOIN pets p ON a.pet_id = p.id
        ORDER BY a.date DESC, a.time DESC
    ''')
    appointments = c.fetchall()
    # Convert sqlite3.Row objects to dicts for JSON serialization in template
    appointments = [dict(a) for a in appointments]
    selected_customer_id = request.form.get('customer_id') if request.method == 'POST' else None
    if request.method == 'POST':
        customer_id = int(request.form['customer_id'])
        appointment_id = request.form.get('appointment_id')
        if not appointment_id:
            conn.close()
            flash('Please select an appointment for this bill.', 'danger')
            return render_template('add_bill.html', customers=customers, customer_details=customer_details, appointments=appointments, selected_customer_id=selected_customer_id, current_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # Fetch appointment details for the selected appointment
        c.execute('''
            SELECT a.service
            FROM appointments a
            WHERE a.id = ?
        ''', (appointment_id,))
        appt = c.fetchone()
        if not appt:
            conn.close()
            flash('Invalid appointment selected.', 'danger')
            return render_template('add_bill.html', customers=customers, customer_details=customer_details, appointments=appointments, selected_customer_id=selected_customer_id, current_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        service = appt[0]
        amount = request.form['amount']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notes = request.form['notes']
        c.execute("INSERT INTO bills (customer_id, appointment_id, service, amount, date, notes) VALUES (?, ?, ?, ?, ?, ?)",
                  (customer_id, appointment_id, service, amount, date, notes))
        bill_id = c.lastrowid
        conn.commit()
        conn.close()
        flash('Bill added successfully!', 'success')
        return redirect(url_for('bills.bill_detail', id=bill_id))
    conn.close()
    return render_template('add_bill.html', customers=customers, customer_details=customer_details, appointments=appointments, selected_customer_id=selected_customer_id, current_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@bills_bp.route('/bills/<int:bill_id>/pdf')
@login_required
def bill_pdf(bill_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT bills.id, customers.name, bills.service, bills.amount, bills.date, bills.notes
        FROM bills
        JOIN customers ON bills.customer_id = customers.id
        WHERE bills.id = ?
    ''', (bill_id,))
    bill = c.fetchone()
    conn.close()
    if bill:
        rendered = render_template('bill_pdf.html', bill=bill)
        pdf = HTML(string=rendered).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=bill_{bill[0]}.pdf'
        return response
    else:
        return "Bill not found", 404

@bills_bp.route('/bills/<int:bill_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bill(bill_id):
    is_admin = session.get('role') == 'admin'
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        service = request.form['service']
        amount = request.form['amount']
        notes = request.form['notes']
        if is_admin:
            date = request.form['date']
            c.execute('UPDATE bills SET service=?, amount=?, notes=?, date=? WHERE id=?',
                      (service, amount, notes, date, bill_id))
        else:
            c.execute('UPDATE bills SET service=?, amount=?, notes=? WHERE id=?',
                      (service, amount, notes, bill_id))
        conn.commit()
        conn.close()
        flash('Bill updated successfully!', 'success')
        # After saving, show empty fields and disable further edits
        return render_template('edit_bill.html', bill=None, saved=True)
    c.execute('''
        SELECT bills.id, customers.name, bills.service, bills.amount, bills.date, bills.notes
        FROM bills
        LEFT JOIN customers ON bills.customer_id = customers.id
        WHERE bills.id=?
    ''', (bill_id,))
    bill = c.fetchone()
    conn.close()
    return render_template('edit_bill.html', bill=bill)

@bills_bp.route('/bills/<int:bill_id>/delete')
@login_required
def delete_bill(bill_id):
    if session.get('role') != 'admin':
        flash('Only admins can delete bills.', 'danger')
        return redirect(url_for('bills.bills'))
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM bills WHERE id=?', (bill_id,))
    conn.commit()
    conn.close()
    flash('Bill deleted successfully!')
    return redirect(url_for('bills.bills'))

@bills_bp.route('/bills/<int:id>')
@login_required
def bill_detail(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT b.id, c.name, b.service, b.amount, b.date, b.notes
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
        WHERE b.id = ?
    ''', (id,))
    bill = c.fetchone()
    conn.close()
    if bill is None:
        abort(404)
    return render_template('bills/detail.html', bill=bill)

@bills_bp.route('/bills/export/csv')
@login_required
def export_bills_csv():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT bills.id, customers.name, bills.service, bills.amount, bills.date, bills.notes
        FROM bills
        LEFT JOIN customers ON bills.customer_id = customers.id
        ORDER BY bills.date DESC
    ''')
    bills = c.fetchall()
    conn.close()
    import csv
    from io import StringIO
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Customer', 'Service', 'Amount', 'Date', 'Notes'])
    cw.writerows(bills)
    output = si.getvalue()
    from flask import Response
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=bills.csv'}
    )

@bills_bp.route('/bills/appointments_for_pets')
@login_required
def appointments_for_pets():
    pet_ids = request.args.get('pet_ids', '').replace('"', '').split(',')
    pet_ids = [pid for pid in pet_ids if pid.isdigit()]
    if not pet_ids:
        return {'appointments': []}
    conn = get_db()
    c = conn.cursor()
    placeholders = ','.join(['?'] * len(pet_ids))
    c.execute(f'''
        SELECT a.id, a.date, a.service, p.pet_name
        FROM appointments a
        JOIN pets p ON a.pet_id = p.id
        WHERE a.pet_id IN ({placeholders})
        ORDER BY a.date DESC, a.time DESC
    ''', pet_ids)
    appointments = [
        {'id': row[0], 'date': row[1], 'service': row[2], 'pet_name': row[3]}
        for row in c.fetchall()
    ]
    conn.close()
    return {'appointments': appointments}
