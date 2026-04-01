from app import db
from datetime import datetime

class UserType(db.Model):
    """User Type Model"""
    __tablename__ = 'user_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    base_template = db.Column(db.String(50), nullable=True)  # Admin, Manager, HR, Staff
    permissions = db.Column(db.Text, nullable=True)  # Store computed JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, base_template=None, permissions=None):
        self.name = name
        self.base_template = base_template
        self.permissions = permissions
    
    def to_dict(self):
        """Convert model to dictionary"""
        import json
        return {
            'id': self.id,
            'name': self.name,
            'base_template': self.base_template,
            'permissions': json.loads(self.permissions) if self.permissions else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserType {self.name}>'