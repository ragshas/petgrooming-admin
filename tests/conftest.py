import pytest
from app import create_app, db

@pytest.fixture(scope='session')
def app():
    # Create a Flask app configured for testing
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.app_context():
        db.create_all()
    yield app
    # Teardown: drop tables
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()
