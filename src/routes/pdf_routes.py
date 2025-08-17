from flask import Blueprint, jsonify, request, send_file
from functools import wraps
from src.models.mess_models import db, MenuPDF, Complaint
from datetime import datetime
import os
import json
import secrets

pdf_bp = Blueprint('pdf', __name__)

def require_admin_auth(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, we'll use a simple check
        # In production, implement proper JWT verification
        return f(*args, **kwargs)
    return decorated_function

@pdf_bp.route('/upload-pdf', methods=['POST'])
@require_admin_auth
def upload_menu_pdf():
    """Upload menu PDF file"""
    try:
        if 'pdf_file' not in request.files:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_FILE',
                    'message': 'No file provided'
                }
            }), 400
        
        file = request.files['pdf_file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_FILE',
                    'message': 'No file selected'
                }
            }), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_FILE',
                    'message': 'Only PDF files are allowed'
                }
            }), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'menu_pdf_{timestamp}.pdf'
        filepath = os.path.join(upload_dir, filename)
        
        # Save file
        file.save(filepath)
        
        # Store in database
        menu_pdf = MenuPDF(
            filename=filename,
            original_filename=file.filename,
            file_size=os.path.getsize(filepath),
            uploaded_by=1  # Default admin ID
        )
        
        db.session.add(menu_pdf)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'PDF uploaded successfully',
            'data': {
                'filename': filename,
                'original_filename': file.filename
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPLOAD_ERROR',
                'message': f'An error occurred while uploading PDF: {str(e)}'
            }
        }), 500

@pdf_bp.route('/current-pdf', methods=['GET'])
@require_admin_auth
def get_current_pdf():
    """Get current menu PDF information"""
    try:
        current_pdf = MenuPDF.query.order_by(MenuPDF.upload_date.desc()).first()
        
        if current_pdf:
            return jsonify({
                'success': True,
                'data': current_pdf.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_PDF',
                    'message': 'No PDF uploaded yet'
                }
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': f'An error occurred while fetching PDF info: {str(e)}'
            }
        }), 500

@pdf_bp.route('/public/current-menu-pdf', methods=['GET'])
def get_public_current_pdf():
    """Get current menu PDF information (public access)"""
    try:
        current_pdf = MenuPDF.query.order_by(MenuPDF.upload_date.desc()).first()
        
        if current_pdf:
            return jsonify({
                'success': True,
                'data': current_pdf.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_PDF',
                    'message': 'No PDF uploaded yet'
                }
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': f'An error occurred while fetching PDF info: {str(e)}'
            }
        }), 500

@pdf_bp.route('/uploads/<filename>')
def serve_pdf(filename):
    """Serve uploaded PDF files"""
    try:
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
        return send_file(os.path.join(upload_dir, filename))
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'FILE_NOT_FOUND',
                'message': 'File not found'
            }
        }), 404
