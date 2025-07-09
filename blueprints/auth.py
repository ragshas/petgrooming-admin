from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth', __name__)

# -----------------------
# Login & Logout
# -----------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=?', (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))

# -----------------------
# User Management (Admin only)
# -----------------------

@auth_bp.route('/users')
def users():
    if session.get('role') != 'admin':
        flash('Only admin can manage users.', 'danger')
        return redirect(url_for('customers.list_customers'))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return render_template('users.html', users=users)

@auth_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if session.get('role') != 'admin':
        flash('Only admin can add users.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        # Use .get with default '0' to ensure unchecked radios/checkboxes are 0
        can_add_customer = int(request.form.get('can_add_customer', 0))
        can_edit_customer = int(request.form.get('can_edit_customer', 0))
        can_delete_customer = int(request.form.get('can_delete_customer', 0))
        can_add_bill = int(request.form.get('can_add_bill', 0))
        can_edit_bill = int(request.form.get('can_edit_bill', 0))
        can_delete_bill = int(request.form.get('can_delete_bill', 0))
        hashed_pw = generate_password_hash(password)
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO users 
                (username, password, role, can_add_customer, can_edit_customer, can_delete_customer, can_add_bill, can_edit_bill, can_delete_bill)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_pw, role, can_add_customer, can_edit_customer, can_delete_customer, can_add_bill, can_edit_bill, can_delete_bill))
            conn.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('auth.users'))
        except Exception:
            flash('Username already exists.', 'danger')
        finally:
            conn.close()
    flash('Please fill out the form to add a new user.', 'info')
    return render_template('add_user.html')

@auth_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if session.get('role') != 'admin':
        flash('Only admin can edit users.', 'danger')
        return redirect(url_for('customers.list_customers'))
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        role = request.form['role']
        can_add_customer = int(request.form.get('can_add_customer', 0))
        can_edit_customer = int(request.form.get('can_edit_customer', 0))
        can_delete_customer = int(request.form.get('can_delete_customer', 0))
        can_add_bill = int(request.form.get('can_add_bill', 0))
        can_edit_bill = int(request.form.get('can_edit_bill', 0))
        can_delete_bill = int(request.form.get('can_delete_bill', 0))
        c.execute('''
            UPDATE users SET role=?, can_add_customer=?, can_edit_customer=?, can_delete_customer=?, 
            can_add_bill=?, can_edit_bill=?, can_delete_bill=? WHERE id=?
        ''', (role, can_add_customer, can_edit_customer, can_delete_customer, can_add_bill, can_edit_bill, can_delete_bill, user_id))
        conn.commit()
        conn.close()
        flash('User updated successfully!', 'success')
        return redirect(url_for('auth.users'))
    c.execute('SELECT * FROM users WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    flash('Please fill out the form to edit the user.', 'info')
    return render_template('edit_user.html', user=user)

@auth_bp.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    if request.method == 'POST':
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username=? AND role="admin"', (admin_username,))
        admin = c.fetchone()
        if admin and check_password_hash(admin[0], admin_password):
            c.execute('DELETE FROM users WHERE id=?', (user_id,))
            conn.commit()
            conn.close()
            flash('User deleted successfully!', 'success')
            return redirect(url_for('auth.users'))
        else:
            flash('Invalid admin credentials.', 'danger')
            conn.close()
            return redirect(url_for('auth.users'))
    return render_template('delete_user.html', user_id=user_id)

@auth_bp.route('/user/<int:user_id>')
def user_detail(user_id):
    if session.get('role') != 'admin':
        flash('Only admin can view user details.', 'danger')
        return redirect(url_for('auth.users'))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.users'))
    return render_template('user_detail.html', user=user)

# -----------------------
# Admin override route
# -----------------------

@auth_bp.route('/admin_auth', methods=['GET', 'POST'])
def admin_auth():
    if request.method == 'POST':
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']
        action = request.form['action']
        target_id = request.form['target_id']
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username=? AND role="admin"', (admin_username,))
        admin = c.fetchone()
        conn.close()
        if admin and check_password_hash(admin[0], admin_password):
            if action == 'edit_customer' and 'pending_edit_customer' in session:
                form_data = session.pop('pending_edit_customer')
                conn = get_db()
                c = conn.cursor()
                c.execute('''
                    UPDATE customers SET name=?, phone=?, email=?, pet_name=?, pet_type=?, notes=? WHERE id=?
                ''', (form_data.get('name'), form_data.get('phone'), form_data.get('email'), form_data.get('pet_name'),
                      form_data.get('pet_type'), form_data.get('notes'), target_id))
                conn.commit()
                conn.close()
                flash('Customer updated successfully (admin override).', 'success')
                return redirect(url_for('customers.list_customers'))
            elif action == 'edit_bill' and 'pending_edit_bill' in session:
                form_data = session.pop('pending_edit_bill')
                conn = get_db()
                c = conn.cursor()
                c.execute('UPDATE bills SET service=?, amount=?, notes=? WHERE id=?',
                    (form_data.get('service'), form_data.get('amount'), form_data.get('notes'), target_id))
                conn.commit()
                conn.close()
                flash('Bill updated successfully (admin override).', 'success')
                return redirect(url_for('bills.bills'))
            # Else: just set override flag for delete
            session['admin_override'] = {'action': action, 'target_id': target_id}
            flash('Admin authorization successful. Please retry your action.', 'success')
            if action in ['edit_customer', 'delete_customer']:
                return redirect(url_for('customers.list_customers'))
            elif action in ['edit_bill', 'delete_bill']:
                return redirect(url_for('bills.bills'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return render_template('admin_auth.html', action=action, target_id=target_id)
    # GET request
    action = request.args.get('action')
    target_id = request.args.get('target_id')
    flash('Please enter admin credentials to proceed.', 'info')
    return render_template('admin_auth.html', action=action, target_id=target_id)

# -----------------------
# Password Reset
# -----------------------

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email=?', (email,))
        user = c.fetchone()
        conn.close()
        if user:
            # Logic to send password reset email
            flash('Password reset link sent to your email.', 'info')
        else:
            flash('Email not found.', 'danger')
    return render_template('reset_password.html')

@auth_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        flash('You must be logged in to change your password.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('New password and confirmation do not match.', 'danger')
            return redirect(url_for('auth.change_password'))

        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username=?', (session['username'],))
        user = c.fetchone()

        if not user or not check_password_hash(user['password'], current_password):
            flash('Current password is incorrect.', 'danger')
            conn.close()
            return redirect(url_for('auth.change_password'))

        hashed_pw = generate_password_hash(new_password)
        c.execute('UPDATE users SET password=? WHERE username=?', (hashed_pw, session['username']))
        conn.commit()
        conn.close()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('change_password.html')
