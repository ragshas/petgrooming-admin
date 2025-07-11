from models import Appointment, db

def get_appointment_by_id(appointment_id):
    return Appointment.query.get(appointment_id)

def create_appointment(data):
    appointment = Appointment(**data)
    db.session.add(appointment)
    db.session.commit()
    return appointment

def update_appointment(appointment_id, data):
    appointment = Appointment.query.get(appointment_id)
    for key, value in data.items():
        setattr(appointment, key, value)
    db.session.commit()
    return appointment

def delete_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return True

def get_appointments_for_pets(pet_ids):
    if not pet_ids:
        return []
    return Appointment.query.filter(Appointment.pet_id.in_(pet_ids)).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
