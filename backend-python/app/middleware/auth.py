import os
import jwt
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from app.models.admin import Admin

def generate_token(admin_id):
    """Generate JWT token"""
    payload = {
        'admin_id': str(admin_id),
        'exp': datetime.utcnow() + timedelta(days=int(os.getenv('JWT_EXPIRE_DAYS', 7)))
    }
    
    token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')
    return token

def token_required(f):
    """Decorator to protect routes with JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing'
            }), 401
        
        try:
            # Decode token
            data = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
            admin_id = data['admin_id']
            
            # Get admin
            admin = Admin.find_by_id(admin_id)
            
            if not admin:
                return jsonify({
                    'success': False,
                    'message': 'Admin not found'
                }), 401
            
            if not admin.get('isActive'):
                return jsonify({
                    'success': False,
                    'message': 'Account is deactivated'
                }), 401
            
            # Store admin in request context
            request.admin = admin
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Token is invalid'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated
