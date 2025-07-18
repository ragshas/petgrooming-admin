from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..decorators import login_required
from ..db import get_db
from datetime import datetime, date as dtdate
import csv
from io import StringIO
from flask import Response
from flask import jsonify

appointments_bp = Blueprint('appointments', __name__)

# API endpoint for FullCalendar events
from flask import jsonify, request
from datetime import timedelta

@appointments_bp.route('/api/appointments', methods=['GET', 'POST'])
@login_required
def api_appointments():
    if request.method == 'GET':
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            SELECT a.id, c.name, p.pet_name, p.size, p.notes, a.service, a.date, a.time, a.duration, a.notes
            FROM appointments a
            JOIN pets p ON a.pet_id = p.id
            JOIN customers c ON p.customer_id = c.id
            ORDER BY a.date, a.time
        ''')
        appointments = c.fetchall()
        conn.close()
        events = []
        for appt in appointments:
            appt_id, customer_name, pet_name, pet_size, pet_notes, service, date, time, duration, notes = appt
            start = f"{date}T{time}"
            end_time = (datetime.strptime(time, '%H:%M') + timedelta(minutes=int(duration))).strftime('%H:%M')
            end = f"{date}T{end_time}"
            events.append({
                'id': appt_id,
                'title': f"{customer_name} - {pet_name} ({service})",
                'start': start,
                'end': end,
                'extendedProps': {
                    'customer_name': customer_name,
                    'pet_name': pet_name,
                    'pet_size': pet_size,
                    'pet_notes': pet_notes,
                    'service': service,
                    'duration': duration,
                    'notes': notes
                }
            })
        return jsonify(events)
    elif request.method == 'POST':
        data = request.get_json()
        conn = get_db()
        c = conn.cursor()
        # If id is present, update, else create
        if data.get('id'):
            # Update appointment
            c.execute('''
                UPDATE appointments SET service=?, date=?, time=?, duration=?, notes=? WHERE id=?
            ''', (data['service'], data['date'], data['time'], data['duration'], data['notes'], data['id']))
            # Update pet size and notes if provided
            if 'pet_size' in data or 'pet_notes' in data:
                c.execute('''
                    SELECT pet_id FROM appointments WHERE id=?
                ''', (data['id'],))
                pet_row = c.fetchone()
                if pet_row:
                    pet_id = pet_row[0]
                    c.execute('''
                        UPDATE pets SET size=?, notes=? WHERE id=?
                    ''', (data.get('pet_size', ''), data.get('pet_notes', ''), pet_id))
            conn.commit()
            conn.close()
            return jsonify({'status': 'updated'})
        else:
            # Find customer and pet IDs (simple lookup, can be improved)
            c.execute('SELECT id FROM customers WHERE name=?', (data['customer_name'],))
            customer_row = c.fetchone()
            if not customer_row:
                c.execute('INSERT INTO customers (name, date_added) VALUES (?, ?)', (data['customer_name'], dtdate.today().strftime('%Y-%m-%d')))
                customer_id = c.lastrowid
            else:
                customer_id = customer_row[0]
            c.execute('SELECT id FROM pets WHERE pet_name=? AND customer_id=?', (data['pet_name'], customer_id))
            pet_row = c.fetchone()
            if not pet_row:
                c.execute('INSERT INTO pets (customer_id, pet_name, size, notes) VALUES (?, ?, ?, ?)', (customer_id, data.get('pet_name', ''), data.get('pet_size', ''), data.get('pet_notes', '')))
                pet_id = c.lastrowid
            else:
                pet_id = pet_row[0]
                # Update pet size and notes if provided
                c.execute('UPDATE pets SET size=?, notes=? WHERE id=?', (data.get('pet_size', ''), data.get('pet_notes', ''), pet_id))
            c.execute('''
                INSERT INTO appointments (customer_id, pet_id, service, date, time, duration, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (customer_id, pet_id, data['service'], data['date'], data['time'], data['duration'], data['notes']))
            conn.commit()
            conn.close()
            return jsonify({'status': 'created'})

# Calendar view route
@appointments_bp.route('/appointments/calendar')
@login_required
def calendar_view():
    return render_template('appointments/calendar.html')

@appointments_bp.route('/appointments')
@login_required
def list_appointments():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    conn = get_db()
    c = conn.cursor()
    # Get total count for pagination
    c.execute('''SELECT COUNT(*) FROM appointments''')
    total_appointments = c.fetchone()[0]
    total_pages = (total_appointments + per_page - 1) // per_page
    # Fetch paginated appointments
    c.execute('''
        SELECT a.id, c.name, p.pet_name, p.pet_type, p.size, a.service, a.date, a.time, a.duration, a.notes
        FROM appointments a
        JOIN pets p ON a.pet_id = p.id
        JOIN customers c ON p.customer_id = c.id
        ORDER BY a.date, a.time
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    appointments = c.fetchall()
    conn.close()
    return render_template('appointments/list.html', appointments=appointments, page=page, total_pages=total_pages)

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
        confirm = request.form.get('confirm')
        today_str = dtdate.today().strftime('%Y-%m-%d')
        # Only use fields for the selected flow
        if customer_type == 'new':
            name = request.form.get('new_name', '').strip()
            phone = request.form.get('new_phone', '').strip()
            email = request.form.get('new_email', '').strip()
            c.execute('SELECT id FROM customers WHERE phone = ?', (phone,))
            row = c.fetchone()
            if row:
                customer_id = row[0]
            else:
                c.execute('INSERT INTO customers (name, phone, email, date_added) VALUES (?, ?, ?, ?)', (name, phone, email, dtdate.today().strftime('%Y-%m-%d')))
                customer_id = c.lastrowid
            new_pet_name = request.form.get('new_pet_name', '').strip()
            new_pet_type = request.form.get('new_pet_type', '').strip()
            new_pet_size = request.form.get('new_pet_size', 'medium')
            pet_notes = request.form.get('new_pet_notes', '').strip()
            c.execute('INSERT INTO pets (customer_id, pet_name, pet_type, size, notes) VALUES (?, ?, ?, ?, ?)', (customer_id, new_pet_name, new_pet_type, new_pet_size, pet_notes))
            pet_id = c.lastrowid
            service = request.form.get('service', '').strip()
            date = request.form.get('date')
            time = request.form.get('time')
            duration = int(request.form.get('duration', 30))
            notes = request.form.get('notes', '').strip()
        else:
            customer_id = request.form.get('customer_id')
            if customer_id:
                c.execute('SELECT id, pet_name FROM pets WHERE customer_id = ?', (customer_id,))
                pets = c.fetchall()
            pet_id = request.form.get('pet_id')
            if not pet_id:
                new_pet_name = request.form.get('existing_new_pet_name', '').strip()
                new_pet_type = request.form.get('existing_new_pet_type', '').strip()
                new_pet_size = request.form.get('existing_new_pet_size', 'medium')
                pet_notes = request.form.get('existing_new_pet_notes', '').strip()
                c.execute('INSERT INTO pets (customer_id, pet_name, pet_type, size, notes) VALUES (?, ?, ?, ?, ?)', (customer_id, new_pet_name, new_pet_type, new_pet_size, pet_notes))
                pet_id = c.lastrowid
            else:
                pet_id = int(pet_id)
            service = request.form.get('service', '').strip()
            date = request.form.get('date')
            time = request.form.get('time')
            duration = int(request.form.get('duration', 30))
            notes = request.form.get('notes', '').strip()
        # Prevent past dates
        if date < today_str:
            conn.close()
            flash('Appointment date cannot be in the past.', 'danger')
            return render_template('appointments/add.html', customers=customers, pets=pets, selected_customer_id=customer_id, form=request.form)
        # Check for double-booking
        c.execute('SELECT id FROM appointments WHERE date=? AND time=? AND pet_id=?', (date, time, pet_id))
        conflict = c.fetchone()
        if conflict and not confirm:
            conn.close()
            flash('Warning: This time slot is already booked for this pet. If you want to proceed, click Save again.', 'warning')
            return render_template('appointments/add.html', customers=customers, pets=pets, selected_customer_id=customer_id, form=request.form)
        c.execute('''
            INSERT INTO appointments (customer_id, pet_id, service, date, time, duration, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, pet_id, service, date, time, duration, notes))
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
    # Fetch appointment with join to match list_appointments indices
    c.execute('''
        SELECT a.id, c.name, p.pet_name, p.pet_type, p.size, a.service, a.date, a.time, a.duration, a.notes, a.customer_id, a.pet_id
        FROM appointments a
        JOIN pets p ON a.pet_id = p.id
        JOIN customers c ON p.customer_id = c.id
        WHERE a.id = ?
    ''', (id,))
    appointment_row = c.fetchone()
    if not appointment_row:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    # Map to dict for template clarity
    appointment = {
        'id': appointment_row[0],
        'customer_name': appointment_row[1],
        'pet_name': appointment_row[2],
        'pet_type': appointment_row[3],
        'pet_size': appointment_row[4],
        'service': appointment_row[5],
        'date': appointment_row[6],
        'time': appointment_row[7],
        'duration': appointment_row[8],
        'notes': appointment_row[9],
        'customer_id': appointment_row[10],
        'pet_id': appointment_row[11],
    }
    customer_id = appointment['customer_id']
    pet_id = appointment['pet_id']
    # Fetch all pet details for this customer
    c.execute('SELECT id, pet_name, pet_type, size, notes FROM pets WHERE customer_id = ?', (customer_id,))
    pets = [tuple(p) for p in c.fetchall()]
    # Find the current pet details
    current_pet = None
    for pet in pets:
        if pet[0] == pet_id:
            current_pet = pet
            break
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        pet_option = request.form.get('pet_option', 'existing')
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
        duration = int(request.form.get('duration', appointment['duration'] if 'duration' in appointment else 30))
        notes = request.form['notes']
        # Pet size handling
        if pet_option == 'existing':
            pet_id = request.form.get('pet_id')
            if not pet_id:
                flash('Please select a pet.', 'danger')
                conn.close()
                return render_template('appointments/edit.html', appointment=appointment, customers=customers, pets=pets, current_pet=current_pet)
            pet_size = request.form.get('pet_size', current_pet[4] if current_pet and len(current_pet) > 4 else 'medium')
            # Update pet size if changed
            c.execute('UPDATE pets SET size=? WHERE id=?', (pet_size, pet_id))
        else:
            new_pet_name = request.form.get('new_pet_name', '').strip()
            new_pet_type = request.form.get('new_pet_type', '').strip()
            new_pet_size = request.form.get('new_pet_size', 'medium')
            pet_notes = request.form.get('new_pet_notes', '').strip()
            if not new_pet_name:
                flash('Please enter a name for the new pet.', 'danger')
                conn.close()
                return render_template('appointments/edit.html', appointment=appointment, customers=customers, pets=pets, current_pet=current_pet)
            c.execute('INSERT INTO pets (customer_id, pet_name, pet_type, size, notes) VALUES (?, ?, ?, ?, ?)', (customer_id, new_pet_name, new_pet_type, new_pet_size, pet_notes))
            pet_id = c.lastrowid
        c.execute('''
            UPDATE appointments
            SET customer_id=?, pet_id=?, service=?, date=?, time=?, duration=?, notes=?
            WHERE id=?
        ''', (customer_id, pet_id, service, date, time, duration, notes, id))
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

@appointments_bp.route('/appointments/export/csv')
@login_required
def export_appointments_csv():
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
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Customer', 'Pet Name', 'Pet Type', 'Service', 'Date', 'Time', 'Notes'])
    cw.writerows(appointments)
    output = si.getvalue()
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=appointments.csv'}
    )
