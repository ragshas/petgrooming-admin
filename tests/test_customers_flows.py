import pytest
from flask import url_for

def test_list_customers(client, auth):
    auth.login()
    response = client.get(url_for('customers.list_customers'))
    assert response.status_code == 200
    assert b'Customers' in response.data

def test_add_customer_redirects_to_appointments(client, auth):
    auth.login()
    response = client.get(url_for('customers.add_customer'))
    assert response.status_code == 302
    assert '/appointments/add' in response.headers['Location']

def test_edit_customer_permission(client, auth):
    # Non-admin should be blocked
    auth.login(role='user')
    response = client.get(url_for('customers.edit_customer', customer_id=1), follow_redirects=True)
    assert b'Only admins can edit customers.' in response.data
    # Admin can access
    auth.login(role='admin')
    response = client.get(url_for('customers.edit_customer', customer_id=1))
    assert response.status_code == 200
    assert b'Edit Customer' in response.data

def test_delete_customer_permission(client, auth):
    # Non-admin should be blocked
    auth.login(role='user')
    response = client.get(url_for('customers.delete_customer', customer_id=1), follow_redirects=True)
    assert b'Only admins can delete customers.' in response.data
    # Admin can delete
    auth.login(role='admin')
    response = client.get(url_for('customers.delete_customer', customer_id=1), follow_redirects=True)
    assert b'Customer deleted successfully!' in response.data

def test_customer_detail(client, auth):
    auth.login()
    response = client.get(url_for('customers.customer_detail', id=1))
    assert response.status_code == 200
    assert b'Customer' in response.data

def test_export_customers_csv(client, auth):
    auth.login()
    response = client.get(url_for('customers.export_customers_csv'))
    assert response.status_code == 200
    assert b'Customer' in response.data
    assert response.mimetype == 'text/csv'

def test_export_pets_csv(client, auth):
    auth.login()
    response = client.get(url_for('customers.export_pets_csv'))
    assert response.status_code == 200
    assert b'Pet Name' in response.data
    assert response.mimetype == 'text/csv'
