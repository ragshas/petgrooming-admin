import pytest
from flask import url_for

def test_list_appointments(client, auth):
    auth.login()
    response = client.get(url_for('appointments.list_appointments'))
    assert response.status_code == 200
    assert b'Appointment' in response.data or b'appointments' in response.data

def test_add_appointment_page(client, auth):
    auth.login()
    response = client.get(url_for('appointments.add_appointment'))
    assert response.status_code == 200
    assert b'Add Appointment' in response.data or b'appointment' in response.data

def test_edit_appointment_permission(client, auth):
    auth.login(role='user')
    response = client.get(url_for('appointments.edit_appointment', id=1), follow_redirects=True)
    # Should be allowed for user, but you can add permission checks if needed
    assert response.status_code == 200
    assert b'Edit Appointment' in response.data or b'appointment' in response.data

def test_delete_appointment(client, auth):
    auth.login(role='admin')
    response = client.post(url_for('appointments.delete_appointment', id=1), follow_redirects=True)
    assert b'Appointment deleted' in response.data

def test_export_appointments_csv(client, auth):
    auth.login()
    response = client.get(url_for('appointments.export_appointments_csv'))
    assert response.status_code == 200
    assert b'Appointment' in response.data or b'appointments' in response.data
    assert response.mimetype == 'text/csv'
