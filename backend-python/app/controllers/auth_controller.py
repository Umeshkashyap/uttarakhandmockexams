from flask import request, jsonify
from app.models.admin import Admin
from app.middleware.auth import generate_token
from bson import ObjectId

def login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        # Validate input
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Please provide username and password'
            }), 400
        
        # Find admin
        admin = Admin.find_by_username(username)
        
        if not admin:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        # Check if active
        if not admin.get('isActive'):
            return jsonify({
                'success': False,
                'message': 'Account is deactivated'
            }), 401
        
        # Verify password
        if not Admin.verify_password(password, admin['password']):
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        # Update last login
        Admin.update_last_login(admin['_id'])
        
        # Generate token
        token = generate_token(admin['_id'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'token': token,
                'admin': {
                    'id': str(admin['_id']),
                    'username': admin['username'],
                    'email': admin['email'],
                    'role': admin['role']
                }
            }
        }), 200
        
    except Exception as e:
        print(f'Login error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Server error during login'
        }), 500

def get_profile():
    """Get current admin profile"""
    try:
        admin = request.admin
        
        return jsonify({
            'success': True,
            'data': {
                'id': str(admin['_id']),
                'username': admin['username'],
                'email': admin['email'],
                'role': admin['role'],
                'lastLogin': admin.get('lastLogin').isoformat() if admin.get('lastLogin') else None,
                'createdAt': admin['createdAt'].isoformat()
            }
        }), 200
        
    except Exception as e:
        print(f'Get profile error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500

def change_password():
    """Change admin password"""
    try:
        admin = request.admin
        data = request.get_json()
        
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Please provide current and new password'
            }), 400
        
        # Get admin with password
        admin_with_password = Admin.find_by_id(admin['_id'])
        
        # Verify current password
        if not Admin.verify_password(current_password, admin_with_password['password']):
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect'
            }), 401
        
        # Update password
        Admin.update_password(admin['_id'], new_password)
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        print(f'Change password error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500
