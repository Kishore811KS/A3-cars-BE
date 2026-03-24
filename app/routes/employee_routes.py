from flask import Blueprint, request, jsonify, send_from_directory
from app import db
from app.models.employee import Employee
from datetime import datetime
import os
import traceback
from werkzeug.utils import secure_filename
import uuid

# Create blueprint
employee_bp = Blueprint('employee', __name__, url_prefix='/api')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, prefix=''):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{prefix}_{uuid.uuid4().hex}_{original_filename}"
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        return filename
    return None

def generate_employee_id():
    """Generate auto-incrementing employee ID"""
    last_employee = Employee.query.order_by(Employee.id.desc()).first()
    if last_employee and last_employee.employee_id:
        try:
            # Extract number from employee_id (e.g., EMP001 -> 1)
            num = int(last_employee.employee_id[3:])
            new_num = num + 1
            return f"EMP{new_num:03d}"
        except:
            return "EMP001"
    return "EMP001"

@employee_bp.route('/employees', methods=['GET'])
def get_employees():
    """Get all employees"""
    try:
        # Optional filter by user_type
        user_type = request.args.get('user_type')
        
        if user_type:
            employees = Employee.query.filter_by(user_type=user_type).order_by(Employee.created_at.desc()).all()
        else:
            employees = Employee.query.order_by(Employee.created_at.desc()).all()
            
        return jsonify([employee.to_dict() for employee in employees]), 200
    except Exception as e:
        print(f"Error in get_employees: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to fetch employees'}), 500

@employee_bp.route('/employees/<int:id>', methods=['GET'])
def get_employee(id):
    """Get a single employee by ID"""
    try:
        employee = Employee.query.get(id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        return jsonify(employee.to_dict()), 200
    except Exception as e:
        print(f"Error in get_employee: {str(e)}")
        return jsonify({'error': 'Failed to fetch employee'}), 500

@employee_bp.route('/employees', methods=['POST'])
def create_employee():
    """Create a new employee"""
    try:
        # Auto-generate employee ID
        employee_id = generate_employee_id()
        
        # Check if email exists
        email = request.form.get('email')
        if not email:
            return jsonify({'error': 'Email is required'}), 400
            
        existing_email = Employee.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'error': 'Email already exists'}), 400
        
        # Get user_type with validation
        user_type = request.form.get('user_type', 'employee')
        valid_user_types = ['admin', 'manager', 'employee', 'hr']
        if user_type not in valid_user_types:
            return jsonify({'error': f'Invalid user_type. Must be one of: {", ".join(valid_user_types)}'}), 400
        
        # Handle date of joining
        date_of_joining = None
        if request.form.get('date_of_joining'):
            try:
                date_of_joining = datetime.strptime(
                    request.form.get('date_of_joining'), '%Y-%m-%d'
                ).date()
            except:
                pass
        
        # Handle file uploads
        aadhar_file = request.files.get('aadhar_attachment')
        pan_file = request.files.get('pan_attachment')
        
        aadhar_filename = None
        pan_filename = None
        
        if aadhar_file and aadhar_file.filename:
            aadhar_filename = save_file(aadhar_file, f"aadhar_{employee_id}")
        
        if pan_file and pan_file.filename:
            pan_filename = save_file(pan_file, f"pan_{employee_id}")
        
        # Create employee
        employee = Employee(
            employee_id=employee_id,
            full_name=request.form.get('full_name'),
            email=email,
            phone_number=request.form.get('phone_number'),
            department=request.form.get('department'),
            designation=request.form.get('designation'),
            date_of_joining=date_of_joining,
            user_type=user_type,
            aadhar_card_number=request.form.get('aadhar_card_number'),
            pan_card_number=request.form.get('pan_card_number'),
            address=request.form.get('address'),
            emergency_contact=request.form.get('emergency_contact'),
            blood_group=request.form.get('blood_group'),
            marital_status=request.form.get('marital_status'),
            aadhar_attachment=aadhar_filename,
            pan_attachment=pan_filename
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify(employee.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_employee: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to create employee'}), 500

@employee_bp.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    """Update an existing employee"""
    try:
        employee = Employee.query.get(id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Check if email exists for other employee
        email = request.form.get('email')
        if email and email != employee.email:
            existing_email = Employee.query.filter_by(email=email).first()
            if existing_email:
                return jsonify({'error': 'Email already exists'}), 400
        
        # Update user_type with validation if provided
        user_type = request.form.get('user_type')
        if user_type:
            valid_user_types = ['admin', 'manager', 'employee', 'hr']
            if user_type not in valid_user_types:
                return jsonify({'error': f'Invalid user_type. Must be one of: {", ".join(valid_user_types)}'}), 400
            employee.user_type = user_type
        
        # Handle date of joining
        if request.form.get('date_of_joining'):
            try:
                date_of_joining = datetime.strptime(
                    request.form.get('date_of_joining'), '%Y-%m-%d'
                ).date()
                employee.date_of_joining = date_of_joining
            except:
                pass
        
        # Handle file uploads
        aadhar_file = request.files.get('aadhar_attachment')
        pan_file = request.files.get('pan_attachment')
        
        # Delete old files if new ones are uploaded
        if aadhar_file and aadhar_file.filename:
            if employee.aadhar_attachment:
                old_file_path = os.path.join(UPLOAD_FOLDER, employee.aadhar_attachment)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            aadhar_filename = save_file(aadhar_file, f"aadhar_{employee.employee_id}")
            employee.aadhar_attachment = aadhar_filename
        
        if pan_file and pan_file.filename:
            if employee.pan_attachment:
                old_file_path = os.path.join(UPLOAD_FOLDER, employee.pan_attachment)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            pan_filename = save_file(pan_file, f"pan_{employee.employee_id}")
            employee.pan_attachment = pan_filename
        
        # Update fields
        if request.form.get('full_name'):
            employee.full_name = request.form.get('full_name')
        if email:
            employee.email = email
        if request.form.get('phone_number'):
            employee.phone_number = request.form.get('phone_number')
        if request.form.get('department'):
            employee.department = request.form.get('department')
        if request.form.get('designation'):
            employee.designation = request.form.get('designation')
        if request.form.get('aadhar_card_number'):
            employee.aadhar_card_number = request.form.get('aadhar_card_number')
        if request.form.get('pan_card_number'):
            employee.pan_card_number = request.form.get('pan_card_number')
        if request.form.get('address'):
            employee.address = request.form.get('address')
        if request.form.get('emergency_contact'):
            employee.emergency_contact = request.form.get('emergency_contact')
        if request.form.get('blood_group'):
            employee.blood_group = request.form.get('blood_group')
        if request.form.get('marital_status'):
            employee.marital_status = request.form.get('marital_status')
        
        db.session.commit()
        
        return jsonify(employee.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_employee: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to update employee'}), 500

@employee_bp.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    """Delete an employee"""
    try:
        employee = Employee.query.get(id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Delete attached files
        if employee.aadhar_attachment:
            file_path = os.path.join(UPLOAD_FOLDER, employee.aadhar_attachment)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        if employee.pan_attachment:
            file_path = os.path.join(UPLOAD_FOLDER, employee.pan_attachment)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({'message': 'Employee deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_employee: {str(e)}")
        return jsonify({'error': 'Failed to delete employee'}), 500

@employee_bp.route('/employees/by-type/<user_type>', methods=['GET'])
def get_employees_by_type(user_type):
    """Get employees by user type"""
    try:
        valid_user_types = ['admin', 'manager', 'employee', 'hr']
        if user_type not in valid_user_types:
            return jsonify({'error': f'Invalid user_type. Must be one of: {", ".join(valid_user_types)}'}), 400
        
        employees = Employee.query.filter_by(user_type=user_type).order_by(Employee.created_at.desc()).all()
        return jsonify([employee.to_dict() for employee in employees]), 200
    except Exception as e:
        print(f"Error in get_employees_by_type: {str(e)}")
        return jsonify({'error': 'Failed to fetch employees'}), 500

@employee_bp.route('/employees/user-types', methods=['GET'])
def get_user_types():
    """Get all available user types"""
    try:
        user_types = ['admin', 'manager', 'employee', 'hr']
        return jsonify({'user_types': user_types}), 200
    except Exception as e:
        print(f"Error in get_user_types: {str(e)}")
        return jsonify({'error': 'Failed to fetch user types'}), 500

@employee_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download attached file"""
    try:
        # Security check to prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            return jsonify({'error': 'Invalid filename'}), 400
            
        return send_from_directory(
            directory=UPLOAD_FOLDER,
            path=filename,
            as_attachment=True,
            download_name=filename
        )
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        print(f"Error in download_file: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500