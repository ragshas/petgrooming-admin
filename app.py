from flask import Flask, render_template, request, redirect, url_for
import sqlite3

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


if __name__ == '__main__':
    app.run(debug=True)
