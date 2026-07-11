from flask import Flask
from routes.dashboard import dashboard_bp
from routes.api import api_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(api_bp)

if __name__ == "__main__":
    # Start the Flask development server
    app.run(debug=True)