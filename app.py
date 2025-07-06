from flask import Flask
from customers import customers_bp
from bills import bills_bp
from auth import auth_bp
from dashboard import dashboard_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a strong secret key

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(bills_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    app.run(debug=True)