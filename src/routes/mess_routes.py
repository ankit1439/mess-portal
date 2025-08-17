from flask import Blueprint, jsonify, request
from src.models.mess_models import (
    db, Vote, Feedback, Complaint, MenuSuggestion, 
    create_user_identifier
)
from datetime import datetime
import hashlib

mess_bp = Blueprint('mess', __name__)

def get_client_ip():
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def get_user_agent():
    """Get user agent from request"""
    return request.headers.get('User-Agent', '')

def create_session_id():
    """Create a unique session ID"""
    timestamp = str(datetime.utcnow().timestamp())
    ip = get_client_ip()
    user_agent = get_user_agent()
    session_data = f"{timestamp}:{ip}:{user_agent}"
    return hashlib.md5(session_data.encode()).hexdigest()

@mess_bp.route('/vote', methods=['POST'])
def submit_vote():
    """Submit a vote for a meal"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['day', 'meal', 'dish']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'Missing required field: {field}'
                    }
                }), 400
        
        # Get client information
        ip_address = get_client_ip()
        user_agent = get_user_agent()
        user_identifier = create_user_identifier(ip_address, user_agent)
        session_id = create_session_id()
        
        # Check if user has already voted for this meal
        existing_vote = Vote.query.filter_by(
            day=data['day'].lower(),
            meal=data['meal'].lower(),
            user_identifier=user_identifier
        ).first()
        
        if existing_vote:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'DUPLICATE_VOTE',
                    'message': 'You have already voted for this meal',
                    'details': {
                        'day': data['day'],
                        'meal': data['meal']
                    }
                }
            }), 400
        
        # Create new vote
        vote = Vote(
            day=data['day'].lower(),
            meal=data['meal'].lower(),
            dish=data['dish'],
            user_identifier=user_identifier,
            ip_address=ip_address,
            session_id=session_id
        )
        
        db.session.add(vote)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vote submitted successfully',
            'vote_id': vote.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while submitting your vote'
            }
        }), 500

@mess_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['feedback_type', 'message']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'Missing required field: {field}'
                    }
                }), 400
        
        # Validate rating if provided
        rating = data.get('rating')
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'INVALID_RATING',
                            'message': 'Rating must be between 1 and 5'
                        }
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_RATING',
                        'message': 'Rating must be a number'
                    }
                }), 400
        
        # Get client information
        ip_address = get_client_ip()
        session_id = create_session_id()
        
        # Create new feedback
        feedback = Feedback(
            feedback_type=data['feedback_type'],
            message=data['message'],
            rating=rating,
            ip_address=ip_address,
            session_id=session_id
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while submitting your feedback'
            }
        }), 500

@mess_bp.route('/complaint', methods=['POST'])
def submit_complaint():
    """Submit a complaint"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['category', 'message', 'urgency']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'Missing required field: {field}'
                    }
                }), 400
        
        # Validate urgency level
        valid_urgency_levels = ['low', 'medium', 'high', 'urgent']
        if data['urgency'].lower() not in valid_urgency_levels:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_URGENCY',
                    'message': f'Urgency must be one of: {", ".join(valid_urgency_levels)}'
                }
            }), 400
        
        # Get client information
        ip_address = get_client_ip()
        session_id = create_session_id()
        
        # Create new complaint
        complaint = Complaint(
            category=data['category'],
            message=data['message'],
            urgency=data['urgency'].lower(),
            ip_address=ip_address,
            session_id=session_id
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Complaint submitted successfully',
            'complaint_id': complaint.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while submitting your complaint'
            }
        }), 500

@mess_bp.route('/menu-suggestion', methods=['POST'])
def submit_menu_suggestion():
    """Submit a menu suggestion"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['dish_name', 'meal_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'Missing required field: {field}'
                    }
                }), 400
        
        # Validate meal type
        valid_meal_types = ['breakfast', 'lunch', 'snacks', 'dinner']
        if data['meal_type'].lower() not in valid_meal_types:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_MEAL_TYPE',
                    'message': f'Meal type must be one of: {", ".join(valid_meal_types)}'
                }
            }), 400
        
        # Get client information
        ip_address = get_client_ip()
        session_id = create_session_id()
        
        # Create new menu suggestion
        suggestion = MenuSuggestion(
            dish_name=data['dish_name'],
            meal_type=data['meal_type'].lower(),
            ingredients=data.get('ingredients', ''),
            description=data.get('description', ''),
            ip_address=ip_address,
            session_id=session_id
        )
        
        db.session.add(suggestion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Menu suggestion submitted successfully',
            'suggestion_id': suggestion.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while submitting your suggestion'
            }
        }), 500

@mess_bp.route('/check-vote', methods=['POST'])
def check_vote_status():
    """Check if user has already voted for a specific meal"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['day', 'meal']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_FIELD',
                        'message': f'Missing required field: {field}'
                    }
                }), 400
        
        # Get client information
        ip_address = get_client_ip()
        user_agent = get_user_agent()
        user_identifier = create_user_identifier(ip_address, user_agent)
        
        # Check if user has already voted
        existing_vote = Vote.query.filter_by(
            day=data['day'].lower(),
            meal=data['meal'].lower(),
            user_identifier=user_identifier
        ).first()
        
        return jsonify({
            'success': True,
            'has_voted': existing_vote is not None,
            'vote_details': existing_vote.to_dict() if existing_vote else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while checking vote status'
            }
        }), 500

# Error handlers
@mess_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': 'Endpoint not found'
        }
    }), 404

@mess_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'METHOD_NOT_ALLOWED',
            'message': 'Method not allowed for this endpoint'
        }
    }), 405

@mess_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'Internal server error'
        }
    }), 500

