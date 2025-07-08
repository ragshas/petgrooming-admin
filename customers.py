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
    page = int(request.args.get('page', 1))
    per_page = 10  # Show 10 customers per page for testing
    offset = (page - 1) * per_page
    conn = get_db()
    c = conn.cursor()
    params = []
    where_clause = ''
    if search:
        where_clause = 'WHERE customers.name LIKE ? OR customers.phone LIKE ?'
        params = [f'%{search}%', f'%{search}%']
    # Get total count for pagination
    count_query = f'SELECT COUNT(DISTINCT customers.id) FROM customers '
    if where_clause:
        count_query += where_clause
    c.execute(count_query, params)
    total_customers = c.fetchone()[0]
    # Get paginated results
    query = f'''
        SELECT customers.id, customers.name, customers.phone, customers.pet_name, customers.date_added,
               COUNT(bills.id) as bill_count
        FROM customers
        LEFT JOIN bills ON customers.id = bills.customer_id
        {where_clause}
        GROUP BY customers.id
        ORDER BY customers.date_added DESC
        LIMIT ? OFFSET ?
    '''
    c.execute(query, params + [per_page, offset])
    customers = c.fetchall()
    conn.close()
    total_pages = (total_customers + per_page - 1) // per_page
    return render_template('customers/list.html', customers=customers, search=search, page=page, total_pages=total_pages)

@customers_bp.route('/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():
    flash('Adding customers directly is now handled via appointments.', 'info')
    return redirect(url_for('appointments.add_appointment'))

@customers_bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    if session.get('role') != 'admin':
        flash('Only admins can edit customers.', 'danger')
        return redirect(url_for('customers.list_customers'))

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
        return redirect(url_for('customers.list_customers'))
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM customers WHERE id=?', (customer_id,))
    conn.commit()
    conn.close()
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('customers.list_customers'))

@customers_bp.route('/customers/<int:id>')
@login_required
def customer_detail(id):
    from datetime import date
    today_str = date.today().strftime('%Y-%m-%d')
    conn = get_db()
    c = conn.cursor()
    # Fetch customer
    c.execute('SELECT id, name, phone, email, date_added FROM customers WHERE id = ?', (id,))
    customer = c.fetchone()
    if not customer:
        conn.close()
        flash('Customer not found.', 'danger')
        return redirect(url_for('customers.list_customers'))
    # Fetch all pets for this customer
    c.execute('SELECT id, pet_name, pet_type, notes FROM pets WHERE customer_id = ?', (id,))
    pets = c.fetchall()
    pets_names = [pet[1] for pet in pets]
    pets_with_appointments = []
    for pet in pets:
        # Upcoming: today or future
        c.execute('''
            SELECT a.id, a.service, a.date, a.time, a.notes
            FROM appointments a
            WHERE a.pet_id = ? AND a.date >= ?
            ORDER BY a.date ASC, a.time ASC
        ''', (pet[0], today_str))
        upcoming = c.fetchall()
        # History: before today
        c.execute('''
            SELECT a.id, a.service, a.date, a.time, a.notes
            FROM appointments a
            WHERE a.pet_id = ? AND a.date < ?
            ORDER BY a.date DESC, a.time DESC
        ''', (pet[0], today_str))
        history = c.fetchall()
        # Fetch bills for this pet
        c.execute('''
            SELECT b.id, b.service, b.amount, b.date, b.notes
            FROM bills b
            JOIN appointments a ON b.appointment_id = a.id
            WHERE a.pet_id = ?
            ORDER BY b.date DESC
        ''', (pet[0],))
        bills = c.fetchall()
        pets_with_appointments.append({
            'id': pet[0],
            'pet_name': pet[1],
            'pet_type': pet[2],
            'notes': pet[3],
            'upcoming': upcoming,
            'history': history,
            'bills': bills
        })
    conn.close()
    return render_template('customers/detail.html', customer=customer, pets=pets_with_appointments, pets_names=pets_names)

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

@customers_bp.route('/pets/export/csv')
@login_required
def export_pets_csv():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT pets.id, customers.name, pets.pet_name, pets.pet_type, pets.notes
        FROM pets
        JOIN customers ON pets.customer_id = customers.id
        ORDER BY customers.name, pets.pet_name
    ''')
    pets = c.fetchall()
    conn.close()
    import csv
    from io import StringIO
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Pet ID', 'Customer', 'Pet Name', 'Pet Type', 'Notes'])
    cw.writerows(pets)
    output = si.getvalue()
    from flask import Response
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=pets.csv'}
    )

@customers_bp.route('/customers/<int:customer_id>/print_pdf')
@login_required
def print_pdf(customer_id):
    # Placeholder: implement PDF export logic here
    flash('PDF export is not implemented yet.', 'info')
    return redirect(url_for('customers.customer_detail', id=customer_id))


