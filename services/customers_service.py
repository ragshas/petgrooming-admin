from models import Customer, db

def get_customer_by_id(customer_id):
    return Customer.query.get(customer_id)

def get_all_customers():
    return Customer.query.order_by(Customer.id.desc()).all()

def create_customer(data):
    customer = Customer(**data)
    db.session.add(customer)
    db.session.commit()
    return customer

def update_customer(customer_id, data):
    customer = Customer.query.get(customer_id)
    for key, value in data.items():
        setattr(customer, key, value)
    db.session.commit()
    return customer

def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return False
    # Delete all pets and their appointments
    from models import Pet, Appointment, db
    for pet in customer.pets:
        # Delete all appointments for this pet
        for appt in pet.appointments:
            db.session.delete(appt)
        db.session.delete(pet)
    db.session.delete(customer)
    db.session.commit()
    return True
