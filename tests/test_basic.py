def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Username' in response.data or b'Login' in response.data

def test_root_redirect(client):
    response = client.get('/')
    # Root should redirect to login for unauthenticated users
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')
