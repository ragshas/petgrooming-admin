from decorators import login_required
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from db import get_db
from datetime import datetime
from weasyprint import HTML


bills_bp = Blueprint('bills', __name__)

@bills_bp.route('/bills')
@login_required
def bills():
    bills_with_names = []
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT bills.id, customers.name, bills.service, bills.amount, bills.date, bills.notes
        FROM bills
        LEFT JOIN customers ON bills.customer_id = customers.id
        ORDER BY bills.date DESC
    ''')
    all_bills = c.fetchall()
    conn.close()
    for bill in all_bills:
        bill = list(bill)
        if bill[1] is None:
            bill[1] = 'Unknown'
        bills_with_names.append(tuple(bill))
    return render_template('bills.html', bills=bills_with_names)

@bills_bp.route('/add_bill', methods=['GET', 'POST'])
@login_required
def add_bill():
    if session.get('role') != 'admin':
        flash('Only admins can add bills.', 'danger')
        return redirect(url_for('bills.bills'))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name FROM customers")
    customers = c.fetchall()
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        service = request.form['service']
        amount = request.form['amount']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notes = request.form['notes']
        c.execute("INSERT INTO bills (customer_id, service, amount, date, notes) VALUES (?, ?, ?, ?, ?)",
                  (customer_id, service, amount, date, notes))
        conn.commit()
        conn.close()
        flash('Bill added successfully!')
        return redirect(url_for('bills.bills'))
    conn.close()
    return render_template('add_bill.html', customers=customers)

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
    if session.get('role') != 'admin':
        flash('Only admins can edit bills.', 'danger')
        return redirect(url_for('bills.bills'))
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        service = request.form['service']
        amount = request.form['amount']
        notes = request.form['notes']
        c.execute('UPDATE bills SET service=?, amount=?, notes=? WHERE id=?',
                  (service, amount, notes, bill_id))
        conn.commit()
        conn.close()
        flash('Bill updated successfully!', 'success')
        # Instead of redirect, show the edit page with the message
        bill = {
            'id': bill_id,
            'service': service,
            'amount': amount,
            'notes': notes
        }
        return render_template('edit_bill.html', bill=bill)
    c.execute('SELECT id, service, amount, notes FROM bills WHERE id=?', (bill_id,))
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
