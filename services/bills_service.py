from models import Bill, db
from sqlalchemy import and_

def get_bill_by_id(bill_id):
    return Bill.query.get(bill_id)

def create_bill(data):
    bill = Bill(**data)
    db.session.add(bill)
    db.session.commit()
    return bill

def update_bill(bill_id, data):
    bill = Bill.query.get(bill_id)
    for key, value in data.items():
        setattr(bill, key, value)
    db.session.commit()
    return bill

def delete_bill(bill_id):
    bill = Bill.query.get(bill_id)
    db.session.delete(bill)
    db.session.commit()
    return True

def get_bills(page=1, per_page=10, customer=None, service=None, start_date=None, end_date=None):
    query = Bill.query
    if customer:
        from models import Customer
        query = query.join(Customer).filter(Customer.name.ilike(f"%{customer}%"))
    if service:
        query = query.filter(Bill.service.ilike(f"%{service}%"))
    if start_date:
        query = query.filter(Bill.date >= start_date)
    if end_date:
        query = query.filter(Bill.date <= end_date)
    total_bills = query.count()
    bills = query.order_by(Bill.date.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return bills, total_bills

def get_all_bills():
    return Bill.query.order_by(Bill.date.desc()).all()
