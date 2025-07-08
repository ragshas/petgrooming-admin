from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db
from decorators import login_required
from datetime import datetime

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/appointments')
@login_required
def list_appointments():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT a.id, c.name, p.pet_name, p.pet_type, a.service, a.date, a.time, a.notes
        FROM appointments a
        JOIN pets p ON a.pet_id = p.id
        JOIN customers c ON p.customer_id = c.id
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
    selected_customer_id = request.form.get('customer_id') if request.method == 'POST' else None
    pets = []
    if request.method == 'POST':
        customer_type = request.form.get('customer_type')
        if customer_type == 'new':
            name = request.form['new_name'].strip()
            phone = request.form['new_phone'].strip()
            email = request.form['new_email'].strip()
            c.execute('SELECT id FROM customers WHERE phone = ?', (phone,))
            row = c.fetchone()
            if row:
                customer_id = row[0]
            else:
                c.execute('INSERT INTO customers (name, phone, email, date_added) VALUES (?, ?, ?, ?)',

                          (name, phone, email, datetime.now().strftime('%Y-%m-%d')))
                customer_id = c.lastrowid
            # Add pet for new customer
            new_pet_name = request.form.get('new_pet_name', '').strip()
            new_pet_type = request.form.get('new_pet_type', '').strip()
            pet_notes = request.form.get('new_pet_notes', '').strip()
            c.execute('INSERT INTO pets (customer_id, pet_name, pet_type, notes) VALUES (?, ?, ?, ?)',
                      (customer_id, new_pet_name, new_pet_type, pet_notes))
            pet_id = c.lastrowid
            service = request.form['service'].strip()
            date = request.form['date']
            time = request.form['time']
            notes = request.form['notes'].strip()
            c.execute('''
                INSERT INTO appointments (customer_id, pet_id, service, date, time, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (customer_id, pet_id, service, date, time, notes))
            conn.commit()
            conn.close()
            flash('Appointment saved successfully!', 'success')
            return redirect(url_for('appointments.list_appointments'))
        else:
            customer_id = request.form.get('customer_id')
            if customer_id:
                c.execute('SELECT id, pet_name FROM pets WHERE customer_id = ?', (customer_id,))
                pets = c.fetchall()
            pet_id = request.form.get('pet_id')
            new_pet_name = request.form.get('new_pet_name', '').strip()
            new_pet_type = request.form.get('new_pet_type', '').strip()
            pet_notes = request.form.get('pet_notes', '').strip()
            if not pet_id and new_pet_name:
                c.execute('INSERT INTO pets (customer_id, pet_name, pet_type, notes) VALUES (?, ?, ?, ?)',
                          (customer_id, new_pet_name, new_pet_type, pet_notes))
                pet_id = c.lastrowid
            elif pet_id:
                pet_id = int(pet_id)
            else:
                flash('Please select or add a pet.', 'danger')
                conn.close()
                return render_template('appointments/add.html', customers=customers, pets=pets, selected_customer_id=customer_id)
            service = request.form['service'].strip()
            date = request.form['date']
            time = request.form['time']
            notes = request.form['notes'].strip()
            c.execute('''
                INSERT INTO appointments (customer_id, pet_id, service, date, time, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (customer_id, pet_id, service, date, time, notes))
            conn.commit()
            conn.close()
            flash('Appointment saved successfully!', 'success')
            return redirect(url_for('appointments.list_appointments'))
    else:
        if selected_customer_id:
            c.execute('SELECT id, pet_name FROM pets WHERE customer_id = ?', (selected_customer_id,))
            pets = c.fetchall()
    conn.close()
    return render_template('appointments/add.html', customers=customers, pets=pets, selected_customer_id=selected_customer_id)

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
    # appointment: (id, customer_id, pet_id, service, date, time, notes)
    customer_id = appointment[1]
    pet_id = appointment[2]
    c.execute('SELECT id, pet_name FROM pets WHERE customer_id = ?', (customer_id,))
    pets = c.fetchall()
    c.execute('SELECT * FROM pets WHERE id = ?', (pet_id,))
    current_pet = c.fetchone()
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        pet_option = request.form.get('pet_option', 'existing')
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
        notes = request.form['notes']
        if pet_option == 'existing':
            pet_id = request.form.get('pet_id')
            if not pet_id:
                flash('Please select a pet.', 'danger')
                conn.close()
                return render_template('appointments/edit.html', appointment=appointment, customers=customers, pets=pets, current_pet=current_pet)
        else:
            new_pet_name = request.form.get('new_pet_name', '').strip()
            new_pet_type = request.form.get('new_pet_type', '').strip()
            pet_notes = request.form.get('new_pet_notes', '').strip()
            if not new_pet_name:
                flash('Please enter a name for the new pet.', 'danger')
                conn.close()
                return render_template('appointments/edit.html', appointment=appointment, customers=customers, pets=pets, current_pet=current_pet)
            c.execute('INSERT INTO pets (customer_id, pet_name, pet_type, notes) VALUES (?, ?, ?, ?)',
                      (customer_id, new_pet_name, new_pet_type, pet_notes))
            pet_id = c.lastrowid
        c.execute('''
            UPDATE appointments
            SET customer_id=?, pet_id=?, service=?, date=?, time=?, notes=?
            WHERE id=?
        ''', (customer_id, pet_id, service, date, time, notes, id))
        conn.commit()
        conn.close()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointments.list_appointments'))
    conn.close()
    return render_template('appointments/edit.html', appointment=appointment, customers=customers, pets=pets, current_pet=current_pet)

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

@appointments_bp.route('/appointments/pets_for_customer/<int:customer_id>')
@login_required
def pets_for_customer(customer_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, pet_name FROM pets WHERE customer_id = ?', (customer_id,))
    pets = c.fetchall()
    conn.close()
    return {'pets': [{'id': p[0], 'name': p[1]} for p in pets]}
