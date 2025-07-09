def test_appointments_list_requires_login(client):
    resp = client.get('/appointments')
    assert resp.status_code == 302
    assert '/login' in resp.headers.get('Location', '')


def test_add_appointment_requires_login(client):
    resp = client.get('/appointments/add')
    assert resp.status_code == 302
    assert '/login' in resp.headers.get('Location', '')
