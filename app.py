from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
from datetime import datetime
from weasyprint import HTML

app = Flask(__name__)

# Home page (simple)
@app.route('/')
def home():
    return redirect(url_for('customers'))  # Redirect to customers list

# Add Customer page (GET + POST)
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        notes = request.form['notes']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO customers (name, phone, email, pet_name, pet_type, notes) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, phone, email, pet_name, pet_type, notes))
        conn.commit()
        conn.close()

        return redirect('/')   # After adding, redirect to home

    return render_template('add_customer.html')

@app.route('/customers')
def customers():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    all_customers = c.fetchall()
    conn.close()
    return render_template('customers.html', customers=all_customers)


@app.route('/add_bill', methods=['GET', 'POST'])
def add_bill():
    conn = sqlite3.connect('database.db')
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
        return redirect(url_for('bills'))
    
    conn.close()
    return render_template('add_bill.html', customers=customers)

@app.route('/bills')
def bills():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        SELECT bills.id, customers.name, bills.service, bills.amount, bills.date, bills.notes
        FROM bills
        JOIN customers ON bills.customer_id = customers.id
        ORDER BY bills.date DESC
    ''')
    all_bills = c.fetchall()
    conn.close()
    return render_template('bills.html', bills=all_bills)

@app.route('/bills/<int:bill_id>/pdf')
def bill_pdf(bill_id):
    conn = sqlite3.connect('database.db')
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

@app.route('/bills/<int:bill_id>/edit', methods=['GET', 'POST'])
def edit_bill(bill_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        service = request.form['service']
        amount = request.form['amount']
        notes = request.form['notes']

        c.execute('UPDATE bills SET service=?, amount=?, notes=? WHERE id=?',
                  (service, amount, notes, bill_id))
        conn.commit()
        conn.close()
        return redirect(url_for('bills'))

    c.execute('SELECT id, service, amount, notes FROM bills WHERE id=?', (bill_id,))
    bill = c.fetchone()
    conn.close()
    return render_template('edit_bill.html', bill=bill)

@app.route('/bills/<int:bill_id>/delete')
def delete_bill(bill_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM bills WHERE id=?', (bill_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('bills'))

@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit_customer(customer_id):
    conn = sqlite3.connect('database.db')
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
        return redirect(url_for('customers'))

    c.execute('SELECT * FROM customers WHERE id=?', (customer_id,))
    customer = c.fetchone()
    conn.close()
    return render_template('edit_customer.html', customer=customer)

@app.route('/customers/<int:customer_id>/delete')
def delete_customer(customer_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM customers WHERE id=?', (customer_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('customers'))

if __name__ == '__main__':
    app.run(debug=True)
