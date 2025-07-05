from flask import Flask, render_template, request, redirect, url_for, make_response, session, flash
import sqlite3
from datetime import datetime
from weasyprint import HTML
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

# Create a Flask web application instance
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a strong secret key

# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Home page route: redirects to the customers list
@app.route('/')
@login_required
def home():
    return redirect(url_for('customers'))  # Redirect to customers list

# Route to add a new customer (supports GET and POST requests)
@app.route('/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():
    # Enforce permission
    if session.get('admin_role') != 'admin' and not session.get('can_add_customer', 1):
        flash('You do not have permission to add customers.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':  # If form is submitted
        # Get form data from the request
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        notes = request.form['notes']

        # Connect to the database and insert the new customer
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO customers (name, phone, email, pet_name, pet_type, notes) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, phone, email, pet_name, pet_type, notes))
        conn.commit()
        conn.close()

        return redirect('/')   # After adding, redirect to home

    # If GET request, show the add customer form
    return render_template('add_customer.html')

# Route to display all customers
@app.route('/customers')
@login_required
def customers():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    all_customers = c.fetchall()  # Get all customers from the database
    conn.close()
    return render_template('customers.html', customers=all_customers)

# Route to add a new bill (supports GET and POST requests)
@app.route('/add_bill', methods=['GET', 'POST'])
@login_required
def add_bill():
    if session.get('admin_role') != 'admin' and not session.get('can_add_bill', 1):
        flash('You do not have permission to add bills.', 'danger')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM customers")
    customers = c.fetchall()  # Get all customers for the dropdown
    
    if request.method == 'POST':  # If form is submitted
        customer_id = request.form['customer_id']
        service = request.form['service']
        amount = request.form['amount']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current date and time
        notes = request.form['notes']
        
        # Insert the new bill into the database
        c.execute("INSERT INTO bills (customer_id, service, amount, date, notes) VALUES (?, ?, ?, ?, ?)",
                  (customer_id, service, amount, date, notes))
        conn.commit()
        conn.close()
        return redirect(url_for('bills'))  # Redirect to bills page
    
    conn.close()
    # If GET request, show the add bill form
    return render_template('add_bill.html', customers=customers)

# Route to display all bills
@app.route('/bills')
@login_required
def bills():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Use LEFT JOIN to show all bills, even if customer is missing
    c.execute('''
        SELECT bills.id, customers.name, bills.service, bills.amount, bills.date, bills.notes
        FROM bills
        LEFT JOIN customers ON bills.customer_id = customers.id
        ORDER BY bills.date DESC
    ''')
    all_bills = c.fetchall()
    conn.close()
    # Replace None customer names with 'Unknown'
    bills_with_names = []
    for bill in all_bills:
        bill = list(bill)
        if bill[1] is None:
            bill[1] = 'Unknown'
        bills_with_names.append(tuple(bill))
    return render_template('bills.html', bills=bills_with_names)

# Route to generate a PDF for a specific bill
@app.route('/bills/<int:bill_id>/pdf')
@login_required
def bill_pdf(bill_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Get the bill and customer info for the given bill_id
    c.execute('''
        SELECT bills.id, customers.name, bills.service, bills.amount, bills.date, bills.notes
        FROM bills
        JOIN customers ON bills.customer_id = customers.id
        WHERE bills.id = ?
    ''', (bill_id,))
    bill = c.fetchone()
    conn.close()

    if bill:
        # Render the bill as HTML and convert to PDF
        rendered = render_template('bill_pdf.html', bill=bill)
        pdf = HTML(string=rendered).write_pdf()

        # Return the PDF as a response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=bill_{bill[0]}.pdf'
        return response
    else:
        return "Bill not found", 404

# Route to edit a bill (supports GET and POST)
@app.route('/bills/<int:bill_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bill(bill_id):
    if session.get('admin_role') != 'admin' and not session.get('can_edit_bill', 1):
        flash('You do not have permission to edit bills.', 'danger')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':  # If form is submitted
        service = request.form['service']
        amount = request.form['amount']
        notes = request.form['notes']

        # Update the bill in the database
        c.execute('UPDATE bills SET service=?, amount=?, notes=? WHERE id=?',
                  (service, amount, notes, bill_id))
        conn.commit()
        conn.close()
        return redirect(url_for('bills'))

    # If GET request, fetch the bill to edit
    c.execute('SELECT id, service, amount, notes FROM bills WHERE id=?', (bill_id,))
    bill = c.fetchone()
    conn.close()
    return render_template('edit_bill.html', bill=bill)

# Route to delete a bill
@app.route('/bills/<int:bill_id>/delete')
@login_required
def delete_bill(bill_id):
    if session.get('admin_role') != 'admin' and not session.get('can_delete_bill', 1):
        flash('You do not have permission to delete bills.', 'danger')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM bills WHERE id=?', (bill_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('bills'))

# Route to edit a customer (supports GET and POST)
@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    if session.get('admin_role') != 'admin' and not session.get('can_edit_customer', 1):
        flash('You do not have permission to edit customers.', 'danger')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':  # If form is submitted
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        notes = request.form['notes']

        # Update the customer in the database
        c.execute('''
            UPDATE customers
            SET name=?, phone=?, email=?, pet_name=?, pet_type=?, notes=?
            WHERE id=?
        ''', (name, phone, email, pet_name, pet_type, notes, customer_id))
        conn.commit()
        conn.close()
        return redirect(url_for('customers'))

    # If GET request, fetch the customer to edit
    c.execute('SELECT * FROM customers WHERE id=?', (customer_id,))
    customer = c.fetchone()
    conn.close()
    return render_template('edit_customer.html', customer=customer)

# Route to delete a customer
@app.route('/customers/<int:customer_id>/delete')
@login_required
def delete_customer(customer_id):
    if session.get('admin_role') != 'admin' and not session.get('can_delete_customer', 1):
        flash('You do not have permission to delete customers.', 'danger')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM customers WHERE id=?', (customer_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('customers'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check user credentials from the database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT id, username, password, role, can_add_customer, can_edit_customer, can_delete_customer, can_add_bill, can_edit_bill, can_delete_bill FROM users WHERE username=?', (username,))
        user = c.fetchone()
        conn.close()
        from werkzeug.security import check_password_hash
        if user and check_password_hash(user[2], password):
            session['admin_logged_in'] = True
            session['admin_username'] = user[1]
            session['admin_role'] = user[3]
            session['can_add_customer'] = user[4]
            session['can_edit_customer'] = user[5]
            session['can_delete_customer'] = user[6]
            session['can_add_bill'] = user[7]
            session['can_edit_bill'] = user[8]
            session['can_delete_bill'] = user[9]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Route to view and manage users
@app.route('/users')
@login_required
def users():
    if session.get('admin_role') != 'admin':
        flash('Only admin can manage users.', 'danger')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return render_template('users.html', users=users)

# Route to add a new user (supports GET and POST requests)
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if session.get('admin_role') != 'admin':
        flash('Only admin can add users.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        can_add_customer = 1 if request.form.get('can_add_customer') else 0
        can_edit_customer = 1 if request.form.get('can_edit_customer') else 0
        can_delete_customer = 1 if request.form.get('can_delete_customer') else 0
        can_add_bill = 1 if request.form.get('can_add_bill') else 0
        can_edit_bill = 1 if request.form.get('can_edit_bill') else 0
        can_delete_bill = 1 if request.form.get('can_delete_bill') else 0
        hashed_pw = generate_password_hash(password)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password, role, can_add_customer, can_edit_customer, can_delete_customer, can_add_bill, can_edit_bill, can_delete_bill) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (username, hashed_pw, role, can_add_customer, can_edit_customer, can_delete_customer, can_add_bill, can_edit_bill, can_delete_bill))
            conn.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('users'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        finally:
            conn.close()
    return render_template('add_user.html')

# Route to edit user roles and permissions (admin only)
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if session.get('admin_role') != 'admin':
        flash('Only admin can edit users.', 'danger')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        role = request.form['role']
        can_add_customer = int(request.form.get('can_add_customer', 0))
        can_edit_customer = int(request.form.get('can_edit_customer', 0))
        can_delete_customer = int(request.form.get('can_delete_customer', 0))
        can_add_bill = int(request.form.get('can_add_bill', 0))
        can_edit_bill = int(request.form.get('can_edit_bill', 0))
        can_delete_bill = int(request.form.get('can_delete_bill', 0))
        c.execute('''UPDATE users SET role=?, can_add_customer=?, can_edit_customer=?, can_delete_customer=?, can_add_bill=?, can_edit_bill=?, can_delete_bill=? WHERE id=?''',
            (role, can_add_customer, can_edit_customer, can_delete_customer, can_add_bill, can_edit_bill, can_delete_bill, user_id))
        conn.commit()
        conn.close()
        flash('User updated successfully!', 'success')
        return redirect(url_for('users'))
    c.execute('SELECT * FROM users WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    return render_template('edit_user.html', user=user)

# Apply login_required to protected routes
app.view_functions['customers'] = login_required(app.view_functions['customers'])
app.view_functions['add_customer'] = login_required(app.view_functions['add_customer'])
app.view_functions['edit_customer'] = login_required(app.view_functions['edit_customer'])
app.view_functions['delete_customer'] = login_required(app.view_functions['delete_customer'])
app.view_functions['bills'] = login_required(app.view_functions['bills'])
app.view_functions['add_bill'] = login_required(app.view_functions['add_bill'])
app.view_functions['edit_bill'] = login_required(app.view_functions['edit_bill'])
app.view_functions['delete_bill'] = login_required(app.view_functions['delete_bill'])
app.view_functions['bill_pdf'] = login_required(app.view_functions['bill_pdf'])

# Run the Flask app if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)