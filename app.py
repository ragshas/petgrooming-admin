from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

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



if __name__ == '__main__':
    app.run(debug=True)
