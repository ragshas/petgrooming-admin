import pytest
from flask import url_for

def test_list_bills(client, auth):
    auth.login()
    response = client.get(url_for('bills.bills'))
    assert response.status_code == 200
    assert b'Bill' in response.data or b'bills' in response.data

def test_add_bill_permission(client, auth):
    auth.login(role='user')
    response = client.get(url_for('bills.add_bill'), follow_redirects=True)
    assert b'Only admins can add bills.' in response.data
    auth.login(role='admin')
    response = client.get(url_for('bills.add_bill'))
    assert response.status_code == 200
    assert b'Add Bill' in response.data or b'bill' in response.data

def test_edit_bill_permission(client, auth):
    auth.login(role='user')
    response = client.get(url_for('bills.edit_bill', bill_id=1), follow_redirects=True)
    assert b'Only admins can edit bills.' in response.data or response.status_code == 403
    auth.login(role='admin')
    response = client.get(url_for('bills.edit_bill', bill_id=1))
    assert response.status_code == 200
    assert b'Edit Bill' in response.data or b'bill' in response.data

def test_delete_bill_permission(client, auth):
    auth.login(role='user')
    response = client.get(url_for('bills.delete_bill', bill_id=1), follow_redirects=True)
    assert b'Only admins can delete bills.' in response.data
    auth.login(role='admin')
    response = client.get(url_for('bills.delete_bill', bill_id=1), follow_redirects=True)
    assert b'Bill deleted successfully' in response.data

def test_bill_detail(client, auth):
    auth.login()
    response = client.get(url_for('bills.bill_detail', id=1))
    assert response.status_code == 200
    assert b'Bill' in response.data

def test_export_bills_csv(client, auth):
    auth.login()
    response = client.get(url_for('bills.export_bills_csv'))
    assert response.status_code == 200
    assert b'Customer' in response.data or b'Bill' in response.data
    assert response.mimetype == 'text/csv'

def test_bill_pdf_export(client, auth):
    auth.login()
    response = client.get(url_for('bills.bill_pdf', bill_id=1))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf' or b'%PDF' in response.data[:10]
