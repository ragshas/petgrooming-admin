from models import Pet, db

def get_pet_by_id(pet_id):
    return Pet.query.get(pet_id)

def create_pet(data):
    pet = Pet(**data)
    db.session.add(pet)
    db.session.commit()
    return pet

def update_pet(pet_id, data):
    pet = Pet.query.get(pet_id)
    for key, value in data.items():
        setattr(pet, key, value)
    db.session.commit()
    return pet

def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return True
