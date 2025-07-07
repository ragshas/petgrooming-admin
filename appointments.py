from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db
from decorators import login_required

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/appointments')
@login_required
def list_appointments():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT a.id, c.name, a.pet_name, a.service, a.date, a.time, a.notes
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        ORDER BY a.date, a.time
    ''')
    appointments = c.fetchall()
    conn.close()
    return render_template('appointments/list.html', appointments=appointments)

@appointments_bp.route('/appointments/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name FROM customers')
    customers = c.fetchall()
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        pet_name = request.form['pet_name']
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
        notes = request.form['notes']
        c.execute('''
            INSERT INTO appointments (customer_id, pet_name, service, date, time, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_id, pet_name, service, date, time, notes))
        conn.commit()
        conn.close()
        flash('Appointment added successfully!', 'success')
        return redirect(url_for('appointments.list_appointments'))
    conn.close()
    return render_template('appointments/add.html', customers=customers)

@appointments_bp.route('/appointments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name FROM customers')
    customers = c.fetchall()
    c.execute('SELECT * FROM appointments WHERE id = ?', (id,))
    appointment = c.fetchone()
    if not appointment:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        pet_name = request.form['pet_name']
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
        notes = request.form['notes']
        c.execute('''
            UPDATE appointments
            SET customer_id=?, pet_name=?, service=?, date=?, time=?, notes=?
            WHERE id=?
        ''', (customer_id, pet_name, service, date, time, notes, id))
        conn.commit()
        conn.close()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointments.list_appointments'))
    conn.close()
    return render_template('appointments/edit.html', appointment=appointment, customers=customers)

@appointments_bp.route('/appointments/delete/<int:id>', methods=['POST'])
@login_required
def delete_appointment(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM appointments WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Appointment deleted.', 'success')
    return redirect(url_for('appointments.list_appointments'))
