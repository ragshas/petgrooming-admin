from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from db import get_db   # reuse the helper

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers')
def customers():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM customers')
    customers = c.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

@customers_bp.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        notes = request.form['notes']

        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO customers (name, phone, email, pet_name, pet_type, notes) VALUES (?, ?, ?, ?, ?, ?)',
                  (name, phone, email, pet_name, pet_type, notes))
        conn.commit()
        conn.close()
        flash('Customer added successfully!')
        return redirect(url_for('customers.customers'))  # note blueprint name

    return render_template('add_customer.html')

@customers_bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit_customer(customer_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
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
        flash('Customer updated successfully!')
        return redirect(url_for('customers.customers'))

    c.execute('SELECT * FROM customers WHERE id=?', (customer_id,))
    customer = c.fetchone()
    conn.close()
    return render_template('edit_customer.html', customer=customer)

@customers_bp.route('/customers/<int:customer_id>/delete')
def delete_customer(customer_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM customers WHERE id=?', (customer_id,))
    conn.commit()
    conn.close()
    flash('Customer deleted successfully!')
    return redirect(url_for('customers.customers'))
