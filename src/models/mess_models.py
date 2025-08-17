from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import hashlib
import secrets

db = SQLAlchemy()

class Vote(db.Model):
    """Model for storing menu voting data"""
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    meal = db.Column(db.String(20), nullable=False)
    dish = db.Column(db.String(100), nullable=False)
    user_identifier = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))
    
    # Unique constraint to prevent duplicate votes
    __table_args__ = (db.UniqueConstraint('day', 'meal', 'user_identifier', name='unique_vote'),)
    
    def __repr__(self):
        return f'<Vote {self.day} {self.meal} {self.dish}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'day': self.day,
            'meal': self.meal,
            'dish': self.dish,
            'user_identifier': self.user_identifier,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_id': self.session_id
        }

class Feedback(db.Model):
    """Model for storing user feedback"""
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    feedback_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, db.CheckConstraint('rating >= 1 AND rating <= 5'))
    ip_address = db.Column(db.String(45), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Feedback {self.feedback_type} {self.rating}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'feedback_type': self.feedback_type,
            'message': self.message,
            'rating': self.rating,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_id': self.session_id
        }

class Complaint(db.Model):
    """Model for storing user complaints"""
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    photos = db.Column(db.Text)  # JSON string of photo URLs
    
    def __repr__(self):
        return f'<Complaint {self.category} {self.urgency}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'message': self.message,
            'urgency': self.urgency,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_id': self.session_id,
            'status': self.status,
            'photos': self.photos
        }

class MenuSuggestion(db.Model):
    """Model for storing menu suggestions"""
    __tablename__ = 'menu_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    dish_name = db.Column(db.String(100), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    ingredients = db.Column(db.Text)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<MenuSuggestion {self.dish_name} {self.meal_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'dish_name': self.dish_name,
            'meal_type': self.meal_type,
            'ingredients': self.ingredients,
            'description': self.description,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_id': self.session_id
        }

class AdminUser(db.Model):
    """Model for admin users"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    @staticmethod
    def hash_password(password):
        """Hash a password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password):
        """Verify a password against the stored hash"""
        try:
            salt, stored_hash = self.password_hash.split(':')
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash == stored_hash
        except ValueError:
            return False

class MenuPDF(db.Model):
    """Model for storing menu PDF files"""
    __tablename__ = 'menu_pdfs'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    
    def __repr__(self):
        return f'<MenuPDF {self.filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'uploaded_by': self.uploaded_by
        }

class AdminSession(db.Model):
    """Model for admin sessions"""
    __tablename__ = 'admin_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    
    # Relationship
    admin = db.relationship('AdminUser', backref=db.backref('sessions', lazy=True))
    
    def __repr__(self):
        return f'<AdminSession {self.admin_id} {self.token[:10]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'token': self.token,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'ip_address': self.ip_address
        }
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    def is_expired(self):
        """Check if the session is expired"""
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    def create_session(cls, admin_id, ip_address, expires_in_hours=1):
        """Create a new admin session"""
        token = cls.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        session = cls(
            admin_id=admin_id,
            token=token,
            expires_at=expires_at,
            ip_address=ip_address
        )
        
        return session

def create_user_identifier(ip_address, user_agent, additional_data=None):
    """Create a unique identifier for a user based on IP and browser fingerprint"""
    identifier_data = f"{ip_address}:{user_agent}"
    if additional_data:
        identifier_data += f":{additional_data}"
    
    # Create a hash of the identifier data
    return hashlib.sha256(identifier_data.encode()).hexdigest()[:32]

def cleanup_expired_sessions():
    """Clean up expired admin sessions"""
    expired_sessions = AdminSession.query.filter(AdminSession.expires_at < datetime.utcnow()).all()
    for session in expired_sessions:
        db.session.delete(session)
    db.session.commit()
    return len(expired_sessions)

