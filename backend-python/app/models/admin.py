from datetime import datetime
from bson import ObjectId
import bcrypt
from app.config.database import Database

class Admin:
    collection_name = 'admins'
    
    @staticmethod
    def get_collection():
        """Get admins collection"""
        db = Database.get_db()
        return db[Admin.collection_name]
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    @staticmethod
    def create(username, email, password, role='admin'):
        """Create new admin"""
        collection = Admin.get_collection()
        
        # Check if admin exists
        if collection.find_one({'username': username}):
            raise ValueError('Admin with this username already exists')
        
        admin_data = {
            'username': username,
            'email': email,
            'password': Admin.hash_password(password),
            'role': role,
            'isActive': True,
            'lastLogin': None,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        
        result = collection.insert_one(admin_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_username(username):
        """Find admin by username"""
        collection = Admin.get_collection()
        return collection.find_one({'username': username})
    
    @staticmethod
    def find_by_id(admin_id):
        """Find admin by ID"""
        collection = Admin.get_collection()
        return collection.find_one({'_id': ObjectId(admin_id)})
    
    @staticmethod
    def update_last_login(admin_id):
        """Update last login timestamp"""
        collection = Admin.get_collection()
        collection.update_one(
            {'_id': ObjectId(admin_id)},
            {'$set': {'lastLogin': datetime.utcnow()}}
        )
    
    @staticmethod
    def update_password(admin_id, new_password):
        """Update admin password"""
        collection = Admin.get_collection()
        collection.update_one(
            {'_id': ObjectId(admin_id)},
            {
                '$set': {
                    'password': Admin.hash_password(new_password),
                    'updatedAt': datetime.utcnow()
                }
            }
        )
