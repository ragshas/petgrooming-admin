def test_bills_list_requires_login(client):
    resp = client.get('/bills')
    assert resp.status_code == 302
    assert '/login' in resp.headers.get('Location', '')


def test_add_bill_requires_login(client):
    resp = client.get('/add_bill')
    assert resp.status_code == 302
    assert '/login' in resp.headers.get('Location', '')
