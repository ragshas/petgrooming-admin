import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    db.init_app(app)

    # Import and register blueprints
    from blueprints.auth import auth_bp
    from blueprints.customers import customers_bp
    from blueprints.appointments import appointments_bp
    from blueprints.bills import bills_bp
    from blueprints.dashboard import dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(bills_bp)
    app.register_blueprint(dashboard_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)