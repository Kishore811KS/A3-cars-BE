from flask import Blueprint, request, jsonify
from app import db
from app.models.current_company import Company
from datetime import datetime
import traceback
import re

# Create blueprint
company_bp = Blueprint('company', __name__, url_prefix='/api/companies')

def validate_gst_number(gst_number):
    """Validate GST number format"""
    if not gst_number:
        return True
    
    # GST number format: 15 characters
    # First 2 digits: state code
    # Next 10: PAN number
    # Next 1: entity number
    # Next 1: checksum digit
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
    return bool(re.match(pattern, gst_number))

def validate_ifsc_code(ifsc_code):
    """Validate IFSC code format"""
    if not ifsc_code:
        return True
    
    # IFSC format: 11 characters, first 4 letters, 5th character 0, last 6 alphanumeric
    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    return bool(re.match(pattern, ifsc_code))

@company_bp.route('/', methods=['GET'])
def get_companies():
    """Get all active companies"""
    try:
        companies = Company.query.filter_by(deleted_at=None).order_by(Company.created_at.desc()).all()
        return jsonify([company.to_dict() for company in companies]), 200
    except Exception as e:
        print(f"Error in get_companies: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to fetch companies'}), 500

@company_bp.route('/list', methods=['GET'])
def get_companies_list():
    """Get simplified list of companies for dropdown (only id and name)"""
    try:
        companies = Company.query.filter_by(deleted_at=None, is_active=True).order_by(Company.name).all()
        companies_list = [{'id': company.id, 'name': company.name} for company in companies]
        return jsonify(companies_list), 200
    except Exception as e:
        print(f"Error in get_companies_list: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to fetch companies list'}), 500

@company_bp.route('/all', methods=['GET'])
def get_all_companies():
    """Get all companies including inactive ones"""
    try:
        companies = Company.query.order_by(Company.created_at.desc()).all()
        return jsonify([company.to_dict() for company in companies]), 200
    except Exception as e:
        print(f"Error in get_all_companies: {str(e)}")
        return jsonify({'error': 'Failed to fetch companies'}), 500

@company_bp.route('/<int:id>', methods=['GET'])
def get_company(id):
    """Get a single company by ID"""
    try:
        company = Company.query.get(id)
        if not company or company.deleted_at:
            return jsonify({'error': 'Company not found'}), 404
        return jsonify(company.to_dict()), 200
    except Exception as e:
        print(f"Error in get_company: {str(e)}")
        return jsonify({'error': 'Failed to fetch company'}), 500

@company_bp.route('/', methods=['POST'])
def create_company():
    """Create a new company"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'address', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Validate GST number if provided
        if data.get('gst_number'):
            if not validate_gst_number(data['gst_number']):
                return jsonify({'error': 'Invalid GST number format'}), 400
            
            # Check if GST number already exists
            existing = Company.query.filter_by(gst_number=data['gst_number'], deleted_at=None).first()
            if existing:
                return jsonify({'error': 'GST number already exists'}), 400
        
        # Validate IFSC code if provided
        if data.get('bank_ifsc'):
            if not validate_ifsc_code(data['bank_ifsc']):
                return jsonify({'error': 'Invalid IFSC code format'}), 400
        
        # Handle registration date
        registration_date = None
        if data.get('registration_date'):
            try:
                registration_date = datetime.strptime(data['registration_date'], '%Y-%m-%d').date()
            except:
                pass
        
        # Create company
        company = Company(
            name=data['name'],
            address=data['address'],
            phone=data['phone'],
            alternate_phone=data.get('alternate_phone'),
            email=data.get('email'),
            gst_number=data.get('gst_number'),
            registration_date=registration_date,
            bank_name=data.get('bank_name'),
            bank_account_number=data.get('bank_account_number'),
            bank_ifsc=data.get('bank_ifsc'),
            bank_branch=data.get('bank_branch'),
            upi_id=data.get('upi_id'),
            notes=data.get('notes'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(company)
        db.session.commit()
        
        return jsonify(company.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_company: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to create company'}), 500

@company_bp.route('/<int:id>', methods=['PUT'])
def update_company(id):
    """Update an existing company"""
    try:
        company = Company.query.get(id)
        if not company or company.deleted_at:
            return jsonify({'error': 'Company not found'}), 404
        
        data = request.get_json()
        
        # Validate GST number if provided
        if data.get('gst_number'):
            if not validate_gst_number(data['gst_number']):
                return jsonify({'error': 'Invalid GST number format'}), 400
            
            # Check if GST number already exists for another company
            existing = Company.query.filter(
                Company.gst_number == data['gst_number'],
                Company.id != id,
                Company.deleted_at == None
            ).first()
            if existing:
                return jsonify({'error': 'GST number already exists'}), 400
        
        # Validate IFSC code if provided
        if data.get('bank_ifsc'):
            if not validate_ifsc_code(data['bank_ifsc']):
                return jsonify({'error': 'Invalid IFSC code format'}), 400
        
        # Handle registration date
        registration_date = company.registration_date
        if data.get('registration_date'):
            try:
                registration_date = datetime.strptime(data['registration_date'], '%Y-%m-%d').date()
            except:
                pass
        
        # Update fields
        company.name = data.get('name', company.name)
        company.address = data.get('address', company.address)
        company.phone = data.get('phone', company.phone)
        company.alternate_phone = data.get('alternate_phone', company.alternate_phone)
        company.email = data.get('email', company.email)
        company.gst_number = data.get('gst_number', company.gst_number)
        company.registration_date = registration_date
        company.bank_name = data.get('bank_name', company.bank_name)
        company.bank_account_number = data.get('bank_account_number', company.bank_account_number)
        company.bank_ifsc = data.get('bank_ifsc', company.bank_ifsc)
        company.bank_branch = data.get('bank_branch', company.bank_branch)
        company.upi_id = data.get('upi_id', company.upi_id)
        company.notes = data.get('notes', company.notes)
        
        if 'is_active' in data:
            company.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify(company.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_company: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to update company'}), 500

@company_bp.route('/<int:id>', methods=['DELETE'])
def delete_company(id):
    """Permanently delete a company"""
    try:
        company = Company.query.get(id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        db.session.delete(company)
        db.session.commit()
        
        return jsonify({'message': 'Company deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_company: {str(e)}")
        return jsonify({'error': 'Failed to delete company'}), 500

@company_bp.route('/<int:id>/soft-delete', methods=['POST'])
def soft_delete_company(id):
    """Soft delete a company"""
    try:
        company = Company.query.get(id)
        if not company or company.deleted_at:
            return jsonify({'error': 'Company not found'}), 404
        
        company.soft_delete()
        
        return jsonify({'message': 'Company deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in soft_delete_company: {str(e)}")
        return jsonify({'error': 'Failed to deactivate company'}), 500

@company_bp.route('/<int:id>/restore', methods=['POST'])
def restore_company(id):
    """Restore a soft-deleted company"""
    try:
        company = Company.query.get(id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        if not company.deleted_at:
            return jsonify({'error': 'Company is already active'}), 400
        
        company.restore()
        
        return jsonify({'message': 'Company restored successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in restore_company: {str(e)}")
        return jsonify({'error': 'Failed to restore company'}), 500

@company_bp.route('/<int:id>/toggle-status', methods=['POST'])
def toggle_company_status(id):
    """Toggle company active/inactive status"""
    try:
        company = Company.query.get(id)
        if not company or company.deleted_at:
            return jsonify({'error': 'Company not found'}), 404
        
        company.is_active = not company.is_active
        db.session.commit()
        
        status = 'activated' if company.is_active else 'deactivated'
        return jsonify({'message': f'Company {status} successfully', 'is_active': company.is_active}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in toggle_company_status: {str(e)}")
        return jsonify({'error': 'Failed to toggle company status'}), 500

@company_bp.route('/search', methods=['GET'])
def search_companies():
    """Search companies by name, GST, phone, or email"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([]), 200
        
        # Search in multiple fields
        companies = Company.query.filter(
            Company.deleted_at == None,
            db.or_(
                Company.name.ilike(f'%{query}%'),
                Company.gst_number.ilike(f'%{query}%'),
                Company.phone.ilike(f'%{query}%'),
                Company.email.ilike(f'%{query}%')
            )
        ).order_by(Company.created_at.desc()).all()
        
        return jsonify([company.to_dict() for company in companies]), 200
        
    except Exception as e:
        print(f"Error in search_companies: {str(e)}")
        return jsonify({'error': 'Failed to search companies'}), 500