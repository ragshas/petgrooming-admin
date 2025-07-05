# Pet Grooming Admin Portal (Day 1)

## Stack
- Python 3.x
- Flask
- SQLite
- HTML/CSS (Bootstrap later)

## Project setup


## How to run
```bash
pip install flask
python app.py

---

## ✏ **Summary: What you did in VS Code**
✅ Installed Python & Flask  
✅ Created project folder in VS Code  
✅ Wrote first Flask app (`app.py`)  
✅ Ran app in VS Code terminal  
✅ Created `README.md` for notes

---

## 🟩 **Ready for Day 2?**
Tomorrow we’ll:
- Set up SQLite database
- Create tables
- Connect Flask to database
- Build HTML form to add customer

> Just say:  
> **“Ready for Day 2”**  
and I’ll prepare beginner‑friendly code & guide!

---

If you face *any* issue (Python, terminal, VS Code):
→ Tell me exactly what you see → I’ll help instantly! 🚀

# 🐾 Pet Grooming Admin Portal

Simple, modular admin portal for a pet grooming business.  
Built with **Python + Flask + SQLite**.  
First goal: manage customer data and billing — and keep adding new features over time.

---

## ✅ Features (so far)
- Add customer with name, contact, and pet details
- Store customer data in SQLite database
- Modular structure, beginner-friendly code

---

## 🛠 Tech stack
- Backend: Python 3.x + Flask
- Database: SQLite
- Frontend: HTML (Bootstrap planned later)
- No JavaScript or TypeScript for now

---

## 📂 Project structure (Day 2)
```plaintext
petgrooming-admin/
├── app.py                # Main Flask app
├── init_db.py            # Script to create database and tables
├── database.db           # SQLite database file
├── templates/
│   └── add_customer.html # HTML form to add customer
├── static/
│   └── style.css         # (empty for now)
└── README.md

View list of saved customers
4️⃣ View all customers:
http://127.0.0.1:5000/customers

Now styled with Bootstrap


# Pet Grooming Admin Portal 🐶✂️

A simple, modular admin portal built in Python (Flask) to help manage a pet grooming business.  
This is the first version — built to be extended over time.

---

## ✅ Current Features

- Add and view customers
- Add and view bills (linked to customers)
- Clean Bootstrap design
- SQLite database for easy local storage

---

## 🚀 Planned Next Features

- Print/export bills as PDF
- Edit/delete bills and customers
- Authentication (admin login)

---

## ⚙️ Tech Stack

- Python 3.x
- Flask
- SQLite
- HTML / Bootstrap (via CDN)

---

## 🏁 How to Run Locally

```bash
# Install dependencies
pip install flask

# Initialize database (creates database.db)
python init_db.py

# Run the server
python app.py

petgrooming-admin/
├── app.py                # Main Flask app
├── init_db.py            # Script to create DB tables
├── database.db           # SQLite DB (ignored by Git)
├── templates/            # HTML templates
│   ├── base.html
│   ├── add_customer.html
│   ├── customers.html
│   ├── add_bill.html
│   └── bills.html
├── static/               # (Optional: future CSS/JS/images)
└── README.md


---

### ✅ **Tip:**  
- Replace `[your name / GitHub username]` with your actual name.
- Add project screenshots later if you want (looks very professional!).

---

## 📦 **Next Steps (as you asked):**

✅ **1️⃣ Print/export bills as PDF**  
- Add a route like `/bills/<id>/pdf` → generate a PDF from bill data.
- Use a library like `pdfkit` or `reportlab` (I’ll guide you).

✅ **2️⃣ Edit/delete bills (and customers)**  
- Add routes & templates to edit / delete.
- Add buttons on bills & customers tables.

✅ **3️⃣ Authentication (login)**  
- Add login page (Flask sessions).
- Only allow logged-in admin to add/edit/delete.

---

## 🏁 **Ready?**
We’ll do them **one by one**, small commits, so you keep learning and stay modular.

> ✔ If you'd like, say:  
✅ *"Yes, start with PDF export"*  
and I’ll write the **complete beginner‑friendly steps + code**.

---

🌱 You're now running a real open‑source‑style project: README, git history, roadmap! 🚀  
Just tell me:  
✅ “Yes, PDF first”  
or  
❓ if you want to do edit/delete first!

# 🐶✂️ Pet Grooming Admin Portal

A simple, modular admin portal built in Python (Flask) to help manage a pet grooming business.  
This is the first version — designed to grow over time.

---

## ✅ Current Features

- Add, view, edit & delete customers
- Add, view, edit & delete bills linked to customers
- Print / export bills to PDF
- Clean Bootstrap interface
- SQLite database (simple, file-based, great for small business)

---

## 🚀 Planned Next Features

- Authentication (admin login)
- Better PDF templates & logos
- Search/filter customers & bills
- Dashboard / analytics

---

## ⚙️ Tech Stack

- Python 3.x
- Flask
- SQLite
- HTML / Bootstrap (via CDN)
- [WeasyPrint](https://weasyprint.org/) (for PDF export)

---

## 🏁 How to Run Locally

```bash
# Install dependencies
pip install flask weasyprint cairocffi

# Initialize database (creates database.db)
python init_db.py

# Run the server
python app.py

⚠ For PDF export:
On Windows, install GTK runtime → add bin folder to PATH.
Guide here

petgrooming-admin/
├── app.py                # Main Flask app
├── init_db.py            # Script to create DB tables
├── database.db           # SQLite DB (ignored by Git)
├── templates/            # HTML templates
│   ├── base.html
│   ├── add_customer.html
│   ├── edit_customer.html
│   ├── customers.html
│   ├── add_bill.html
│   ├── edit_bill.html
│   ├── bills.html
│   └── bill_pdf.html
├── static/               # (Optional: CSS/JS/images)
└── README.md
