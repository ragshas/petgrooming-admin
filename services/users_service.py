from models import User, db
from werkzeug.security import check_password_hash, generate_password_hash

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def create_user(data):
    if 'password' in data:
        data['password'] = generate_password_hash(data['password'])
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return user

def update_user(user_id, data):
    user = User.query.get(user_id)
    if 'password' in data:
        data['password'] = generate_password_hash(data['password'])
    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()
    return user

def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return True

def check_user_password(user, password):
    return check_password_hash(user.password, password)

def get_all_users():
    return User.query.all()

def create_default_admin():
    from models import User
    from werkzeug.security import generate_password_hash
    if not User.query.filter_by(username='admin').first():
        user = User(
            username='admin',
            password=generate_password_hash('administrator'),
            role='admin',
            can_add_customer=True,
            can_edit_customer=True,
            can_delete_customer=True,
            can_add_bill=True,
            can_edit_bill=True,
            can_delete_bill=True
        )
        db.session.add(user)
        db.session.commit()
