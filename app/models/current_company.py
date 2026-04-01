from app import db
from datetime import datetime

class Company(db.Model):
    """Company Model"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    alternate_phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    
    # GST Information
    gst_number = db.Column(db.String(15), unique=True)  # 15 characters GSTIN format
    
    # Registration Details
    registration_date = db.Column(db.Date)
    
    # Banking Details
    bank_name = db.Column(db.String(100))
    bank_account_number = db.Column(db.String(50))
    bank_ifsc = db.Column(db.String(11))
    bank_branch = db.Column(db.String(100))
    upi_id = db.Column(db.String(100))
    
    # Additional
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Soft delete
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def soft_delete(self):
        """Soft delete the company"""
        self.deleted_at = datetime.utcnow()
        self.is_active = False
        db.session.commit()
    
    def restore(self):
        """Restore a soft-deleted company"""
        self.deleted_at = None
        self.is_active = True
        db.session.commit()
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'alternate_phone': self.alternate_phone,
            'email': self.email,
            'gst_number': self.gst_number,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'bank_name': self.bank_name,
            'bank_account_number': self.bank_account_number,
            'bank_ifsc': self.bank_ifsc,
            'bank_branch': self.bank_branch,
            'upi_id': self.upi_id,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Company {self.name}>'