def test_customers_list_requires_login(client):
    # Unauthenticated access should redirect to login
    resp = client.get('/customers')
    assert resp.status_code == 302
    assert '/login' in resp.headers.get('Location', '')


def test_add_customer_requires_login(client):
    # GET /add_customer should redirect to login
    resp = client.get('/add_customer')
    assert resp.status_code == 302
    assert '/login' in resp.headers.get('Location', '')
