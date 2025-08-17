import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.mess_models import db, AdminUser
from src.routes.user import user_bp
from src.routes.mess_routes import mess_bp
from src.routes.admin_routes import admin_bp
from src.routes.pdf_routes import pdf_bp

# Flask app setup
app = Flask(__name__, static_folder="src/static", template_folder="src/static")
app.config['SECRET_KEY'] = 'mess_portal_secret_key_2024_secure_random'

# Database setup (Postgres from Railway)
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or "sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300
}

# Init DB
db.init_app(app)

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Register routes
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(mess_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(pdf_bp, url_prefix='/api')

# Create tables + default admin on startup
with app.app_context():
    try:
        db.create_all()
        admin_user = AdminUser.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = AdminUser(
                username='admin',
                password_hash=AdminUser.hash_password('admin123'),
                email='admin@mess.portal',
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Default admin created: username='admin', password='admin123'")
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        # Continue without crashing the app

# Serve frontend (index.html + static files)
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

# Health check
@app.route("/api/health")
def health_check():
    return {"status": "healthy", "message": "Mess Portal Backend is running"}

# Entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
