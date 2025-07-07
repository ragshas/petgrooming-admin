from decorators import login_required
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from db import get_db   # reuse the helper
from datetime import datetime

customers_bp = Blueprint('customers', __name__)

# customers.py

@customers_bp.route('/customers')
@login_required
def list_customers():
    search = request.args.get('search', '').strip()
    conn = get_db()
    c = conn.cursor()
    if search:
        c.execute('''
            SELECT id, name, phone, pet_name, date_added
            FROM customers
            WHERE name LIKE ? OR phone LIKE ?
            ORDER BY date_added DESC
        ''', (f'%{search}%', f'%{search}%'))
    else:
        c.execute('''
            SELECT id, name, phone, pet_name, date_added
            FROM customers
            ORDER BY date_added DESC
        ''')
    customers = c.fetchall()
    conn.close()
    return render_template('customers/list.html', customers=customers, search=search)



@customers_bp.route('/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        notes = request.form['notes']
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO customers (name, phone, email, pet_name, pet_type, notes, date_added) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  (name, phone, email, pet_name, pet_type, notes, date_added))
        conn.commit()
        conn.close()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('customers.customers'))  # note blueprint name

    return render_template('add_customer.html')

@customers_bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    if session.get('role') != 'admin':
        flash('Only admins can edit customers.', 'danger')
        return redirect(url_for('customers.customers'))

    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        notes = request.form['notes']
        c.execute('''
            UPDATE customers
            SET name=?, phone=?, email=?, pet_name=?, pet_type=?, notes=?
            WHERE id=?
        ''', (name, phone, email, pet_name, pet_type, notes, customer_id))
        conn.commit()
        conn.close()
        flash('Customer updated successfully!', 'success')
        # Instead of redirect, show the edit page with the message
        customer = {
            'id': customer_id,
            'name': name,
            'phone': phone,
            'email': email,
            'pet_name': pet_name,
            'pet_type': pet_type,
            'notes': notes
        }
        return render_template('edit_customer.html', customer=customer)

    c.execute('SELECT * FROM customers WHERE id=?', (customer_id,))
    customer = c.fetchone()
    conn.close()
    return render_template('edit_customer.html', customer=customer)

@customers_bp.route('/customers/<int:customer_id>/delete')
@login_required
def delete_customer(customer_id):
    if session.get('role') != 'admin':
        flash('Only admins can delete customers.', 'danger')
        return redirect(url_for('customers.customers'))
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM customers WHERE id=?', (customer_id,))
    conn.commit()
    conn.close()
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('customers.customers'))

@customers_bp.route('/customers/<int:id>')
@login_required
def customer_detail(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name, phone, email, pet_name, pet_type, notes, date_added FROM customers WHERE id = ?', (id,))
    customer = c.fetchone()
    conn.close()
    if customer:
        return render_template('customers/detail.html', customer=customer)
    else:
        flash('Customer not found.', 'danger')
        return redirect(url_for('customers.customers'))  # adjust if your list route name is different
    
@customers_bp.route('/customers/export/csv')
@login_required
def export_customers_csv():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT id, name, phone, email, pet_name, pet_type, date_added, notes
        FROM customers
        ORDER BY date_added DESC
    ''')
    customers = c.fetchall()
    conn.close()

    import csv
    from io import StringIO
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Name', 'Phone', 'Email', 'Pet Name', 'Pet Type', 'Date Added', 'Notes'])  # header
    cw.writerows(customers)

    output = si.getvalue()
    from flask import Response
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=customers.csv'}
    )


