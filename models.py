from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash
from app import db

# This file will be imported by app.py

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(32))
    email = db.Column(db.String(128))
    notes = db.Column(db.Text)
    pets = db.relationship('Pet', backref='customer', lazy=True)

class Pet(db.Model):
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    pet_name = db.Column(db.String(128), nullable=False)
    pet_type = db.Column(db.String(64))
    size = db.Column(db.String(32))
    notes = db.Column(db.Text)
    appointments = db.relationship('Appointment', backref='pet', lazy=True)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    service = db.Column(db.String(128), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer)
    notes = db.Column(db.Text)

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    service = db.Column(db.String(128), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(128))
    role = db.Column(db.String(32), default='user')
    can_add_customer = db.Column(db.Boolean, default=True)
    can_edit_customer = db.Column(db.Boolean, default=False)
    can_delete_customer = db.Column(db.Boolean, default=False)
    can_add_bill = db.Column(db.Boolean, default=True)
    can_edit_bill = db.Column(db.Boolean, default=False)
    can_delete_bill = db.Column(db.Boolean, default=False)
