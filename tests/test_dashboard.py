import pytest
from flask import url_for

def test_dashboard_access(client, auth):
    auth.login()
    response = client.get(url_for('dashboard.dashboard'))
    assert response.status_code == 200
    assert b'Dashboard' in response.data or b'dashboard' in response.data
    # Check for some stats keywords
    assert b'Customers' in response.data or b'Bills' in response.data or b'Revenue' in response.data
